

import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import About from "./About";
import App from "./App";
import Home from "./Home";
import NotFound from "./NotFound";
import "./animations.css";
import { Auth } from "./auth";

const root = createRoot(document.getElementById("root")!);
root.render(
    <BrowserRouter>
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/auth" element={<Auth onAuthSuccess={() => { window.location.href = "/app"; }} />} />
            <Route path="/app" element={<App />} />
            <Route path="*" element={<NotFound />} />
        </Routes>
    </BrowserRouter>
);
