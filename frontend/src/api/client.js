import axios from "axios";

const apiBase = import.meta.env.VITE_API_BASE || "";

export const api = axios.create({
  baseURL: apiBase,
  timeout: 20000
});

export function handleError(error) {
  if (error.response?.data?.error) return error.response.data.error;
  if (error.message) return error.message;
  return "请求失败";
}
