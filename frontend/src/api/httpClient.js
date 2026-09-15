// ไฟล์นี้รวมฟังก์ชันเรียก REST API และจัดการข้อผิดพลาดกลางของ frontend
const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export async function request(path, options = {}) {
  // ส่งคำขอไป backend และคืนผลลัพธ์เป็น JSON
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || "ไม่สามารถเชื่อมต่อข้อมูลได้");
  }
  return response.status === 204 ? null : response.json();
}
