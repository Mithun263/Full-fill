import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import ProductList from "./components/ProductList";
import ProgressBar from "./components/ProgressBar";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* 🔹 Header */}
        <header className="app-header">
          <h2>⚙️ Acme Product Importer</h2>
          <nav>
            <Link to="/">Upload</Link>
            <Link to="/products">Products</Link>
          </nav>
        </header>

        {/* 🔹 Page Content */}
        <main className="app-content">
          <Routes>
            <Route path="/" element={<FileUpload />} />
            <Route path="/products" element={<ProductList />} />
          </Routes>
        </main>

        {/* 🔹 Footer */}
        <footer className="app-footer">
          <p>© {new Date().getFullYear()} Acme Importer • FastAPI + React</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
