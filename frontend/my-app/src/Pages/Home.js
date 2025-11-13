import React, { useState } from "react";
import FileUpload from "../components/FileUpload";
import ProductList from "../components/ProductList";

export default function Home() {
  const [refresh, setRefresh] = useState(false);

  return (
    <div className="container">
      <h1>Acme Product Importer</h1>
      <FileUpload onUploadComplete={() => setRefresh(!refresh)} />
      <ProductList key={refresh} />
    </div>
  );
}
