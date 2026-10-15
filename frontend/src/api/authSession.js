// App-level session state. The server validates the Google session and role.
// No role is read from localStorage or accepted from an untrusted URL.
import { ref } from "vue";

export const authEnabled = ref(false);
export const currentUser = ref(null);
let statusPromise = null;

export async function loadAuthStatus() {
  if (!statusPromise) {
    statusPromise = fetch("/api/auth/status", {
      credentials: "same-origin",
      cache: "no-store",
    })
      .then(async (response) => {
        if (!response.ok) throw new Error("Auth status unavailable");
        const status = await response.json();
        authEnabled.value = status.enabled === true;
        return authEnabled.value;
      })
      .catch(() => {
        // Server-side RBAC remains authoritative if this request fails.
        // Do not pretend an account is authorized.
        authEnabled.value = false;
        return false;
      });
  }
  return statusPromise;
}

export async function loadCurrentUser() {
  try {
    const response = await fetch("/api/auth/me", {
      credentials: "same-origin",
      cache: "no-store",
    });
    if (!response.ok) {
      currentUser.value = null;
      return null;
    }
    const user = await response.json();
    if (user.role !== "owner" && user.role !== "employee") {
      currentUser.value = null;
      return null;
    }
    currentUser.value = user;
    return user;
  } catch {
    currentUser.value = null;
    return null;
  }
}

export async function logout() {
  await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "same-origin",
  });
  currentUser.value = null;
}
