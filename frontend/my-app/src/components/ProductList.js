import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/products";

function ProductList() {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [limit] = useState(50);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, [page, search]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/all`, {
        params: { skip: page * limit, limit, search },
      });
      setProducts(res.data);
    } catch (err) {
      console.error("Error fetching:", err);
    } finally {
      setLoading(false);
    }
  };

  const deleteProduct = async (id) => {
    if (!window.confirm("Delete this product?")) return;
    await axios.delete(`${API_URL}/${id}`);
    fetchProducts();
  };

  const bulkDelete = async () => {
    if (!window.confirm("⚠️ Delete ALL products? This cannot be undone!")) return;
    await axios.delete(`${API_URL}/bulk-delete`);
    fetchProducts();
  };

  return (
    <div className="product-list">
      <h3>📦 Product List</h3>
      <div className="actions">
        <input
          type="text"
          placeholder="Search by name or SKU..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button onClick={fetchProducts}>Search</button>
        <button className="danger" onClick={bulkDelete}>Delete All</button>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table className="product-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>SKU</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>{p.sku}</td>
                <td>{p.description}</td>
                <td>
                  <button onClick={() => deleteProduct(p.id)}>🗑️ Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="pagination">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>⬅ Prev</button>
        <span>Page {page + 1}</span>
        <button onClick={() => setPage(page + 1)}>Next ➡</button>
      </div>
    </div>
  );
}

export default ProductList;
