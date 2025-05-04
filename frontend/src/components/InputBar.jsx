import React, { useState, useRef, useEffect } from "react";
import { toast } from "react-toastify";
import styles from "./InputBar.module.css";
import axios from "axios";

const MAX_LENGTH = 300000;

const InputBar = ({ onSend }) => {
    const [input, setInput] = useState("");
    const textareaRef = useRef(null);

    const handleSend = () => {
        if (!input.trim()) return;

        if (input.length > MAX_LENGTH) {
            toast.error("Message is too long. Max 300,000 characters.");
            return;
        }

        onSend(input);
        setInput("");
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = "auto";
            textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
        }
    }, [input]);

    const handleClearHistory = async () => {
        try {
            await axios.post("http://localhost:8000/api/clear");
            toast.success("History cleared successfully.");
            window.location.reload();
        } catch (err) {
            console.error("Failed to clear history:", err);
            toast.error("Failed to clear history.");
        }
    };

    return (
        <div className={styles.inputBarContainer}>
            <button className={styles.clearButton} onClick={handleClearHistory}>
                Clear History
            </button>
            <div className={styles.inputWrapper}>
                <textarea
                    ref={textareaRef}
                    className={styles.textarea}
                    placeholder="Ask anything ... "
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={1}
                />
                <button className={styles.sendButton} onClick={handleSend}>
                    ➤
                </button>
            </div>
        </div>
    );
};

export default InputBar;
