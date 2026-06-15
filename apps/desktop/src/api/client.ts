const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const apiBaseUrl = configuredBaseUrl.replace(/\/$/, "");
const apiPrefix = "/api/v1";

export class ApiRequestError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

type JsonRequest = {
  method?: "GET" | "POST" | "PUT";
  body?: unknown;
};

function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${apiBaseUrl}${apiPrefix}${normalizedPath}`;
}

async function readFailureMessage(response: Response): Promise<string> {
  const fallbackMessage = `${response.status} ${response.statusText}`.trim();

  try {
    const failurePayload = (await response.json()) as { detail?: unknown };
    if (typeof failurePayload.detail === "string") {
      return failurePayload.detail;
    }
    return fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}

export async function requestJson<ResponseBody>(
  path: string,
  request: JsonRequest = {}
): Promise<ResponseBody> {
  const headers = new Headers();

  if (request.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(buildApiUrl(path), {
    method: request.method ?? "GET",
    headers,
    body: request.body === undefined ? undefined : JSON.stringify(request.body)
  });

  if (!response.ok) {
    throw new ApiRequestError(response.status, await readFailureMessage(response));
  }

  return (await response.json()) as ResponseBody;
}

export async function requestText(path: string): Promise<string> {
  const response = await fetch(buildApiUrl(path));

  if (!response.ok) {
    throw new ApiRequestError(response.status, await readFailureMessage(response));
  }

  return response.text();
}
