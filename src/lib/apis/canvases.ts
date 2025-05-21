import { WEBUI_BASE_URL } from '$lib/constants';

export interface Canvas {
  id: string;
  user_id: string;
  chat_id?: string | null;
  title: string;
  data: any;
  created_at: number;
  updated_at: number;
}

export interface CanvasFormData {
  title?: string;
  data?: any;
  chat_id?: string | null;
}

const getAuthToken = (): string | null => {
  if (typeof localStorage !== 'undefined') {
    return localStorage.token;
  }
  return null;
};

export const getCanvasById = async (id: string): Promise<Canvas> => {
  const token = getAuthToken();
  const response = await fetch(`${WEBUI_BASE_URL}/api/v1/canvases/${id}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    console.error('Error fetching canvas by ID:', errorData);
    throw new Error(errorData.detail || `Failed to fetch canvas ${id}`);
  }
  return response.json();
};

export const updateCanvasById = async (id: string, canvasData: CanvasFormData): Promise<Canvas> => {
  const token = getAuthToken();
  const response = await fetch(`${WEBUI_BASE_URL}/api/v1/canvases/${id}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(canvasData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    console.error('Error updating canvas by ID:', errorData);
    throw new Error(errorData.detail || `Failed to update canvas ${id}`);
  }
  return response.json();
};

export const createCanvas = async (canvasData: CanvasFormData): Promise<Canvas> => {
  const token = getAuthToken();
  const response = await fetch(`${WEBUI_BASE_URL}/api/v1/canvases/new`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(canvasData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    console.error('Error creating canvas:', errorData);
    throw new Error(errorData.detail || 'Failed to create canvas');
  }
  return response.json();
};

export const getCanvases = async (): Promise<Canvas[]> => {
  const token = getAuthToken();
  const response = await fetch(`${WEBUI_BASE_URL}/api/v1/canvases/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    console.error('Error fetching canvases:', errorData);
    throw new Error(errorData.detail || 'Failed to fetch canvases');
  }
  return response.json();
};

export const deleteCanvasById = async (id: string): Promise<void> => {
  const token = getAuthToken();
  const response = await fetch(`${WEBUI_BASE_URL}/api/v1/canvases/${id}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    console.error('Error deleting canvas by ID:', errorData);
    throw new Error(errorData.detail || `Failed to delete canvas ${id}`);
  }
  // DELETE requests often return 204 No Content or a success boolean
  // We don't expect a JSON body here usually for a successful delete
};

export async function processCanvasContent(
    id: string,
    content: any, // string or JSON object
    command: string,
    model_id?: string
): Promise<{ processed_content: string }> {
    const token = getAuthToken();
    const response = await fetch(`${WEBUI_BASE_URL}/api/v1/canvases/${id}/process_content`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({ content, command, model_id })
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to process canvas content and parse error' }));
        throw new Error(errorData.detail || 'Failed to process canvas content');
    }
    return response.json();
}
