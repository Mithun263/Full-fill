import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

// -------------------------------
// Upload CSV file
// -------------------------------
export const uploadCSV = async (file) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(`${API_URL}/products/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    return response.data; // { added: X }
  } catch (error) {
    console.error("Error uploading CSV:", error.response?.data || error.message);
    throw error;
  }
};

// -------------------------------
// Fetch all products
// -------------------------------
export const getProducts = async () => {
  try {
    const response = await axios.get(`${API_URL}/products/all`);
    return response.data; // Array of products
  } catch (error) {
    console.error("Error fetching products:", error.response?.data || error.message);
    throw error;
  }
};

// -------------------------------
// Edit a single product
// -------------------------------
export const editProduct = async (productId, key, newValue) => {
  try {
    const response = await axios.put(`${API_URL}/products/edit`, null, {
      params: { product_id: productId, key, new_value: newValue },
    });
    return response.data;
  } catch (error) {
    console.error("Error editing product:", error.response?.data || error.message);
    throw error;
  }
};

// -------------------------------
// Bulk delete products
// -------------------------------
export const deleteProducts = async (productIds) => {
  try {
    const response = await axios.delete(`${API_URL}/products/bulk_delete`, {
      params: { product_ids: productIds },
    });
    return response.data;
  } catch (error) {
    console.error("Error deleting products:", error.response?.data || error.message);
    throw error;
  }
};
