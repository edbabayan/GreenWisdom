import React from "react";
import MessageBubble from "./MessageBubble";
import styles from "./ChatWindow.module.css";

const ChatWindow = ({ messages }) => {
    return (
        <div className={styles.chatWindow}>
            {messages.map((msg, index) => (
                <MessageBubble
                    key={index}
                    role={msg.role}
                    text={msg.text}
                    isSkeleton={msg.text === "..."}
                />
            ))}
        </div>
    );
};

export default ChatWindow;