// ไฟล์เชื่อมต่อข้อมูลสรุปแค็ตตาล็อก โดยใช้ API คลังเป็นแหล่งข้อมูลเดียว
import { inventoryApi } from "./inventoryApi";

export async function getCatalogSummary() {
  return inventoryApi.getSummary();
}
