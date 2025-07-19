# Core imports
import hashlib
import logging
import os
import pickle
import signal
import sys
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
import platform

# Model imports
import torch
# --> NEW: AI Memory and Database imports
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

# Flask imports
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from model import GPT, GPTConfig

# --> NEW: Load environment variables for Supabase
load_dotenv()

print("[Void Z1] chat_api.py starting up...")
# Configure logging ONCE
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("void-z1")

# --- Environment settings ---
MODEL_PATH = os.getenv('MODEL_PATH', 'out/model.pt')
VOCAB_PATH = os.getenv('VOCAB_PATH', 'data/void/vocab.pkl')
META_PATH = os.getenv('META_PATH', 'data/void/meta.pkl')
PORT = int(os.getenv('PORT', 10000))
INPUT_PATH = 'data/input.txt'

# Fast failure for missing required files
for required_file, description in [
    (MODEL_PATH, 'Model weights'),
    (VOCAB_PATH, 'Vocabulary file'),
    (META_PATH, 'Meta configuration')
]:
    if not os.path.exists(required_file):
        print(f"[FATAL] Missing required file: {description} at {required_file}")
        import sys
        sys.exit(1)


# --> NEW: Supabase and AI Memory settings
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # Produces 384-dim vectors
# Note: The SQL schema was updated for 768 dims. Let's adjust it in code for now.
# A better fix would be to align the model and schema.
# For example, use 'all-mpnet-base-v2' for 768-dim.

# --- Security settings ---
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "1000"))

# Rate limiting
request_counts = defaultdict(lambda: {"count": 0, "window_start": time.time()})

# Global state
model = None
stoi = None
itos = None
training_status = {'status': 'idle', 'message': ''}
# --> NEW: Supabase client and embedding model
supabase: Client = None
embedding_model = None

# --> NEW: Function to initialize Supabase client


def init_supabase():
    global supabase
    if SUPABASE_URL and SUPABASE_KEY:
        logger.info("Initializing Supabase client...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        logger.warning(
            "Supabase environment variables not set. "
            "Database features will be disabled."
        )

# --> NEW: Function to load the embedding model
def load_embedding_model():
    global embedding_model
    try:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}", exc_info=True)


def check_required_files():
    """Check if all required files exist."""
    required_files = {
        MODEL_PATH: "Model weights",
        VOCAB_PATH: "Vocabulary file",
        META_PATH: "Meta configuration"
    }

    missing_files = []
    for file_path, description in required_files.items():
        if not os.path.exists(file_path):
            missing_files.append(f"{description}: {file_path}")

    if missing_files:
        error_msg = "Missing required files:\n" + "\n".join(missing_files)
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def load_model():
    """Load the model and its configuration."""
    global model, stoi, itos
    try:
        logger.info("Loading model configuration...")
        with open(META_PATH, 'rb') as f:
            meta = pickle.load(f)

        with open(VOCAB_PATH, 'rb') as f:
            chars, stoi = pickle.load(f)

        logger.info("Initializing model...")
        config = GPTConfig(**meta)
        model = GPT(config)

        logger.info("Loading model weights...")
        model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
        model.eval()

        itos = {i: ch for ch, i in stoi.items()}
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        model = None
        stoi = None
        itos = None


def get_client_identifier():
    """Get a unique identifier for the client."""
    identifier = str(request.headers.get("X-Forwarded-For", request.remote_addr))
    return hashlib.sha256(identifier.encode()).hexdigest()


def rate_limit(f):
    """Rate limiting decorator."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_id = get_client_identifier()
        current_time = time.time()
        client_data = request_counts[client_id]

        # Reset window if expired
        if current_time - client_data["window_start"] > RATE_LIMIT_WINDOW:
            client_data["count"] = 0
            client_data["window_start"] = current_time

        # Check rate limit
        if client_data["count"] >= RATE_LIMIT_REQUESTS:
            response = jsonify(
                {
                    "error": "Rate limit exceeded",
                    "reset_time": datetime.fromtimestamp(
                        client_data["window_start"] + RATE_LIMIT_WINDOW
                    ).isoformat(),
                }
            )
            response.status_code = 429
            return response

        client_data["count"] += 1
        return f(*args, **kwargs)

    return decorated_function


def add_security_headers(response):
    """Add security headers to response."""
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self' 'unsafe-inline'",
        "Strict-Transport-Security": ("max-age=31536000; includeSubDomains"),
    }
    for key, value in headers.items():
        response.headers[key] = value
    return response


# --- Timeout helpers ---
class TimeoutException(Exception):
    """Exception raised when operation times out."""

    pass


def timeout_handler(signum, frame):
    """Signal handler for timeouts."""
    raise TimeoutException()


class time_limit:
    """Context manager for time limits."""

    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        if platform.system() != "Windows":
            # Only use SIGALRM on non-Windows systems
            if hasattr(signal, "SIGALRM") and hasattr(signal, "alarm"):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        if platform.system() != "Windows":
            if hasattr(signal, "alarm"):
                signal.alarm(0)


# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_BUILD_DIR = os.path.join(BASE_DIR, 'frontend', 'dist', 'public')

app = Flask(
    __name__,
    static_folder=FRONTEND_BUILD_DIR,
    static_url_path=''
)
CORS(app)
app.after_request(add_security_headers)

# --- Model and vocab loading ---


def try_load_model():
    try:
        logger.info("Loading model and vocabulary...")
        with open(VOCAB_PATH, "rb") as f:
            chars, stoi = pickle.load(f)
        itos = {i: ch for i, ch in stoi.items()}
        vocab_size = len(chars)
        logger.info(f"Loaded vocabulary with size {vocab_size}")
        with open(META_PATH, "rb") as f:
            meta = pickle.load(f)
        logger.info("Loaded meta configuration")
        config = GPTConfig(
            vocab_size=vocab_size,
            block_size=meta.get("block_size", 64),
            n_layer=meta.get("n_layer", 4),
            n_head=meta.get("n_head", 4),
            n_embd=meta.get("n_embd", 128),
            dropout=0.0,
            bias=meta.get("bias", True),
        )
        logger.info("Loading model weights...")
        model = GPT(config)
        model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        model.eval()
        logger.info("Model loaded successfully")
        return model, stoi, itos
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        return None, None, None


model, stoi, itos = try_load_model()


# --- Health check ---


@app.route("/health", endpoint="health_check")
def health_check():
    """Temporary health check endpoint for Render deployment debug."""
    logger.info(
        "/health endpoint called - always returning 200 for Render health check."
    )
    return jsonify({"status": "ok", "message": "Void Z1 is running."}), 200


@app.route("/train", methods=["POST"])
def train():
    data = request.get_json()
    text = data.get("text", "")
    user_id = data.get("user_id", None)
    if not text:
        return jsonify({"error": "No training text provided."}), 400
    # Simulate training (no-op for dummy model)
    logger.info(f"Received training text from user {user_id}: {text[:50]}...")
    return jsonify({"status": "ok", "message": "Training started (simulated)."})


@app.route("/")
def serve_index():
    """Serve the main frontend for Void Z1."""
    return send_from_directory(FRONTEND_BUILD_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    file_path = os.path.join(FRONTEND_BUILD_DIR, path)
    if not os.path.isfile(file_path):
        # For SPA routing, fallback to index.html
        return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
    response = send_from_directory(FRONTEND_BUILD_DIR, path)
    if path.endswith((".js", ".css", ".html")):
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# --- Chat endpoint ---


@app.route("/chat", methods=["POST"])
@rate_limit
def chat():
    """Handle chat requests with AI memory."""
    if not model or not stoi or not itos:
        # Dummy response if model is not loaded
        logger.warning(
            "Model not loaded, returning dummy response."
        )
        return jsonify({
            "text": "[AI is not trained yet. Please train the model with your own data.]"
        })

    data = request.get_json()
    prompt = data.get("prompt", "")
    user_id = data.get("user_id")  # We'll get this from the frontend

    if not prompt or len(prompt) > MAX_PROMPT_LENGTH:
        return jsonify({"error": "Invalid prompt"}), 400
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        # --> NEW: AI Memory Logic
        memory_context = ""
        if supabase and embedding_model:
            try:
                # 1. Create an embedding for the user's prompt
                prompt_embedding = embedding_model.encode(prompt).tolist()

                # 2. Find relevant past conversations
                matches = supabase.rpc('match_relevant_chats', {
                    'query_embedding': prompt_embedding,
                    'match_threshold': 0.75,
                    'match_count': 5,
                    'request_user_id': user_id
                }).execute()

                if matches.data:
                    logger.info(f"Found {len(matches.data)} relevant memories for user {user_id}")
                    # Create a context string from the memories
                    memory_context = "Relevant past conversations:\n"
                    for match in reversed(matches.data):  # reversed to keep chronological order
                        memory_context += f"User: {match['message']}\nAI: {match['response']}\n"
                    memory_context += "\n---\nCurrent Conversation:\n"

            except Exception as e:
                logger.error(f"Error fetching AI memory: {e}", exc_info=True)

        # Combine memory with the current prompt
        final_prompt = memory_context + prompt

        # Generate response from the model
        with time_limit(30):
            encoded_prompt = torch.tensor([
                stoi[c] for c in final_prompt
            ], dtype=torch.long, device='cpu').unsqueeze(0)
            with torch.no_grad():
                generated_encoded = model.generate(
                    encoded_prompt,
                    max_new_tokens=data.get("max_new_tokens", 100),
                    temperature=data.get("temperature", 0.8),
                    top_k=data.get("top_k", 200)
                )
            response_text = "".join([itos[i] for i in generated_encoded[0].tolist()])

        # --> NEW: Save the new conversation and its embedding to the database
        if supabase and embedding_model:
            try:
                # We use the original prompt's embedding
                supabase.table('chats').insert({
                    'user_id': user_id,
                    'message': prompt,
                    'response': response_text,
                    'embedding': prompt_embedding
                }).execute()
            except Exception as e:
                logger.error(
                    f"Error saving chat to Supabase: {e}", exc_info=True
                )
                if 'embedding' in str(e):
                    return jsonify({
                        "error": (
                            "Database is missing the 'embedding' column. "
                            "Please update your schema."
                        )
                    }), 500

            return jsonify({"text": response_text})

    except TimeoutException:
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        logger.error(f"Error during chat generation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


def cleanup_memory():
    """Clean up memory after each request."""
    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        import gc
        gc.collect()
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


@app.after_request
def after_request(response):
    cleanup_memory()
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
    )
    return response


def server_error(e):
    logger.error(f"Server Error: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


# --- Utility to check Supabase function existence ---
def check_supabase_function_exists():
    if not supabase:
        return False
    try:
        # Try a dry run of the function with dummy data
        dummy_embedding = [0.0] * 384
        result = supabase.rpc('match_relevant_chats', {
            'query_embedding': dummy_embedding,
            'match_threshold': 0.0,
            'match_count': 1,
            'request_user_id': (
                '00000000-0000-0000-0000-000000000000'
            )
        }).execute()
        if hasattr(result, 'status_code') and result.status_code == 404:
            logger.warning(
                "Supabase function 'match_relevant_chats' does not exist or "
                "is not accessible."
            )
            return False
        return True
    except Exception as e:
        logger.warning(
            f"Supabase function 'match_relevant_chats' check failed: {e}"
        )
        return False


def check_embedding_column():
    if not supabase:
        return False
    try:
        # Try to insert a dummy row with embedding, rollback immediately
        from uuid import uuid4
        dummy_id = str(uuid4())
        dummy = {
            'id': dummy_id,
            'user_id': '00000000-0000-0000-0000-000000000000',
            'message': 'test',
            'response': 'test',
            'embedding': [0.0] * 384
        }
        # Use upsert to avoid duplicate errors, and delete after
        supabase.table('chats').upsert(dummy).execute()
        supabase.table('chats').delete().eq('id', dummy_id).execute()
        return True
    except Exception as e:
        logger.error(
            "Supabase 'chats' table is missing the 'embedding' column or it "
            "is misconfigured: %s",
            e
        )
        return False


if __name__ == '__main__':
    check_required_files()
    init_supabase()  # --> NEW: Initialize Supabase
    load_embedding_model()  # --> NEW: Load the embedding model
    load_model()
    # Check for match_relevant_chats function
    if supabase:
        check_supabase_function_exists()
        check_embedding_column()
    logger.info(f"Starting server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
