// API utility to connect frontend chat to backend AI

/**
 * Send a chat message to the AI backend and get a response.
 * This now includes the user_id for memory lookup.
 */
export async function sendChatMessage(
    prompt: string,
    user_id: string,
    options?: { max_new_tokens?: number; temperature?: number }
) {
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt,
                user_id,
                max_new_tokens: options?.max_new_tokens ?? 100,
                temperature: options?.temperature ?? 0.8,
            }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Unknown error");
        }
        const data = await response.json();
        return data.text;
    } catch (e: any) {
        throw new Error(e.message || "Network error. Backend unreachable.");
    }
}

/**
 * Send plain text to the backend to train the AI.
 * Returns status JSON.
 */
export async function trainAI(text: string) {
    try {
        const response = await fetch("/train", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        return await response.json();
    } catch (e: any) {
        return { error: e.message || "Network error. Backend unreachable." };
    }
}

/**
 * Get the current training status from the backend.
 * Returns status JSON.
 */
export async function getTrainingStatus() {
    try {
        const response = await fetch("/status");
        return await response.json();
    } catch (e: any) {
        return { status: "error", message: e.message || "Network error." };
    }
}
