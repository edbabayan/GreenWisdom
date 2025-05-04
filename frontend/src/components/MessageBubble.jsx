import React, { useState } from "react";
import styles from "./MessageBubble.module.css";

const MAX_PREVIEW_LENGTH = 300;

const MessageBubble = ({ role, text, isSkeleton }) => {
    const safeText = typeof text === "string" ? text : String(text);
    const [expanded, setExpanded] = useState(false);

    const isUser = role === "user";
    const shouldTruncate = isUser && safeText.length > MAX_PREVIEW_LENGTH;
    const displayText =
        !shouldTruncate || expanded
            ? safeText
            : safeText.slice(0, MAX_PREVIEW_LENGTH) + "…";

    const toggleExpanded = () => setExpanded((prev) => !prev);

    return (
        <div
            className={`${styles.message} ${
                isUser ? styles.user : styles.ai
            }`}
        >
            {isSkeleton ? (
                <>
                    <div className={styles.skeleton}></div>
                    <div className={styles.skeleton}></div>
                    <div className={styles.skeleton} style={{ width: "60%" }}></div>
                </>
            ) : (
                <>
                    <span>{displayText}</span>
                    {shouldTruncate && (
                        <span
                            className={styles.showMoreToggle}
                            onClick={toggleExpanded}
                        >
                            {expanded ? " Show less" : " Show more"}
                        </span>
                    )}
                </>
            )}
        </div>
    );
};

export default MessageBubble;