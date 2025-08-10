import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const rawGeneratedText = location.state?.generatedText || "";
  const userPrompt = location.state?.userPrompt || "";

  // Enhanced cleaning and formatting function
  const formatDialogue = (text) => {
    if (!text.trim()) {
      return <div className="text-yellow-400 italic">No dialogue was generated</div>;
    }

    // Clean the text first
    let cleanedText = text
      .replace(/[{}[\]\\]/g, '') // Remove JSON artifacts
      .replace(/<\/?[^>]+(>|$)/g, '') // Remove HTML tags
      .replace(/\*\s*\*/g, '') // Remove asterisks
      .replace(/_/g, '') // Remove underscores
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    // Split into potential dialogue lines
    return cleanedText.split(/(?=\b(?:Alex|Taylor):)/i).map((line, i) => {
      line = line.trim();
      if (!line) return null;

      // Handle malformed lines
      const colonIndex = line.indexOf(':');
      if (colonIndex === -1) {
        return (
          <div key={i} className="text-gray-400 italic mb-2">
            {line}
          </div>
        );
      }

      const character = line.substring(0, colonIndex).trim();
      let dialogue = line.substring(colonIndex + 1).trim();

      // Clean up dialogue content
      dialogue = dialogue
        .replace(/^\W+/, '') // Remove leading punctuation
        .replace(/\s+/g, ' ') // Normalize spaces
        .trim();

      return (
        <div key={i} className="mb-3 flex">
          <strong className="text-blue-400 min-w-[60px]">{character}:</strong>
          <span className="ml-2 text-gray-100 flex-1">
            {dialogue || <span className="italic text-gray-400">...</span>}
          </span>
        </div>
      );
    }).filter(Boolean);
  };

  if (!rawGeneratedText) {
    return (
      <div className="container mx-auto p-4 max-w-2xl">
        <p className="text-red-500">No generated text to display.</p>
        <button 
          onClick={() => navigate("/")} 
          className="mt-4 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <h1 className="text-3xl font-bold mb-6 text-white">Dialogue Results</h1>
      
      <section className="mb-8 bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-2 text-gray-300">Your Prompt</h2>
        <div className="bg-gray-700 p-4 rounded text-white">
          {userPrompt || "No prompt provided"}
        </div>
      </section>
      
      <section className="mb-8 bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-2 text-gray-300">Generated Dialogue</h2>
        <div className="bg-gray-900 p-4 rounded text-green-300 font-mono">
          {formatDialogue(rawGeneratedText)}
        </div>
      </section>
      
      <div className="flex flex-wrap gap-4">
        <button 
          onClick={() => navigate("/")} 
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded flex-1"
        >
          Generate New Dialogue
        </button>
        <button 
          onClick={() => {
            navigator.clipboard.writeText(rawGeneratedText);
            alert('Dialogue copied to clipboard!');
          }}
          className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-6 rounded flex-1"
        >
          Copy Raw Output
        </button>
      </div>
    </div>
  );
}