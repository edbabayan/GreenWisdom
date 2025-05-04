import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import ChatWindow from "./components/ChatWindow";
import InputBar from "./components/InputBar";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
function App() {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const socketRef = useRef(null);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");
        socket.onopen = () => {
            console.log(":white_check_mark: WebSocket connected");
        };
        socket.onmessage = (event) => {
            const delta = event.data;
            if (delta) {
                setMessages((prev) => {
                    const updated = [...prev];
                    const lastIndex = updated.length - 1;
                    if (updated[lastIndex]?.role === "ai") {
                        updated[lastIndex] = {
                            ...updated[lastIndex],
                            text: updated[lastIndex].text + delta,
                        };
                    }
                    return updated;
                });
            }
        };
        socket.onerror = (err) => {
            console.error("WebSocket error:", err);
        };
        socket.onclose = () => {
            console.log(":x: WebSocket disconnected");
        };
        socketRef.current = socket;
        return () => {
            socket.close();
        };
    }, []);

    const sendQuestion = (question) => {
        if (!question.trim()) return;
        if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
            console.error("WebSocket is not connected.");
            return;
        }
        const userMessage = { role: "user", text: question };
        const aiPlaceholder = { role: "ai", text: "" };
        setMessages((prev) => [...prev, userMessage, aiPlaceholder]);
        setIsLoading(true);
        socketRef.current.send(JSON.stringify({ message: question }));
    };


    const sendQuestionViaHttp = async (question) => {
        if (!question.trim()) return;

        const userMessage = { role: "user", text: question };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        try {
            const response = await axios.post("http://localhost:8000/api/ask", {
                query: question,
            });

            console.log("response", response)

            const assistantMessage = { role: "ai", text: response.data.answer };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (err) {
            console.error("HTTP request failed:", err);
        } finally {
            setIsLoading(false);
        }
    };


    const loadHistory = async () => {
        try {
            const res = await axios.get("http://localhost:8000/api/history");
            const rawHistory = res.data;

            if (Array.isArray(rawHistory) && rawHistory.length === 1 && Object.keys(rawHistory[0]).length === 0) {
                console.log("Empty history received. Skipping...");
                return;
            }

            console.log("rawHistory", rawHistory[0]);

            const formattedHistory = rawHistory.flatMap((item) => [
                { role: "user", text: item.user },
                { role: "ai", text: item.assistant },
            ]);
            setMessages(formattedHistory);
        } catch (err) {
            console.error("Failed to load history:", err);
        }
    };

    useEffect(() => {
        loadHistory();
    }, []);
    
    return (
        <div className="app-container">
            <ToastContainer position="top-center" />
            <ChatWindow messages={messages} isLoading={isLoading} />
            <InputBar onSend={sendQuestion} />
        </div>
    );
}
export default App;
