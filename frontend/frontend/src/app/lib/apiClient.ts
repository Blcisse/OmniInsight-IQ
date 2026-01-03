import axios from "axios";

// Next.js runtime env: expose via NEXT_PUBLIC_API_BASE_URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
});

// Simple response/error interceptors (optional extension point)
apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    // You can add global error logging here
    return Promise.reject(error);
  }
);

export default apiClient;
