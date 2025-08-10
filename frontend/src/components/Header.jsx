import React from "react";
import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="bg-gray-800 text-white p-4">
      <nav className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">DeepScript AI</Link>
        <div>
          <Link to="/" className="mr-4 hover:underline">Generate</Link>
          <Link to="/result" className="hover:underline">Result</Link>
        </div>
      </nav>
    </header>
  );
}
