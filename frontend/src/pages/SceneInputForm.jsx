import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function SceneInputForm() {
  const [prompt, setPrompt] = useState("");
  const [emotion, setEmotion] = useState("neutral");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const emotions = ["neutral", "happy", "sad", "angry", "romantic"]; // Match your model's emotions

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      alert("Please enter a prompt.");
      return;
    }
    setLoading(true);
    
    try {
      const API_BASE_URL = process.env.NODE_ENV === "development" 
        ? "http://127.0.0.1:8000" 
        : "";

      const response = await fetch(`${API_BASE_URL}/api/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          prompt,
          emotion,
          num_turns: 4, // Fewer turns for better quality
          max_turn_length: 100,
          temperature: 0.7
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `HTTP error: ${response.status}`);
      }

      const data = await response.json();
      navigate("/result", {
        state: { 
          generatedText: formatOutput(data.generated_text), 
          userPrompt: prompt 
        },
      });
    } catch (err) {
      alert("Generation error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Clean up the output format
  const formatOutput = (text) => {
    try {
      // Try to parse as JSON if needed
      const parsed = JSON.parse(text);
      return parsed.text || text;
    } catch {
      // Remove malformed JSON artifacts
      return text.replace(/{.*?}/g, '')
                .replace(/\\"/g, '"')
                .trim();
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-2xl font-bold mb-4">Generate Screenplay Dialogue</h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-2 font-medium">Dialogue Prompt:</label>
          <textarea
            rows={6}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Example: Alex was staring at her eyes"
            className="w-full p-3 border rounded-lg resize-none"
            disabled={loading}
          />
        </div>
        
        <div className="mb-4">
          <label className="block mb-2 font-medium">Emotion:</label>
          <select
            value={emotion}
            onChange={(e) => setEmotion(e.target.value)}
            className="w-full p-2 border rounded"
            disabled={loading}
          >
            {emotions.map(emo => (
              <option key={emo} value={emo}>
                {emo.charAt(0).toUpperCase() + emo.slice(1)}
              </option>
            ))}
          </select>
        </div>
        
        <button
          type="submit"
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded disabled:opacity-50"
          disabled={loading || !prompt.trim()}
        >
          {loading ? "Generating..." : "Generate Dialogue"}
        </button>
      </form>
    </div>
  );
}