// Get API base URL from localStorage or environment variable
const getApiBase = () => {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
};

// 错误处理辅助函数
async function handleApiResponse<T>(response: Response, actionName: string): Promise<T> {
  if (!response.ok) {
    let errorMessage = `${actionName} 失败`;
    let errorDetail = '';

    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorDetail = errorData.detail;
      } else if (errorData.message) {
        errorDetail = errorData.message;
      }
    } catch {
      // 如果无法解析JSON，尝试获取文本
      try {
        const text = await response.text();
        if (text) errorDetail = text;
      } catch {
        // 什么也不做
      }
    }

    // 构建详细错误信息
    const statusMessages: Record<number, string> = {
      400: '请求参数错误',
      404: '接口地址不存在',
      500: '服务器内部错误',
      502: '服务器连接失败',
      503: '服务不可用',
    };

    if (statusMessages[response.status]) {
      errorMessage = `${actionName} 失败 (${response.status}: ${statusMessages[response.status]})`;
    } else if (response.status) {
      errorMessage = `${actionName} 失败 (${response.status})`;
    }

    if (errorDetail) {
      errorMessage += `: ${errorDetail}`;
    }

    // 特别处理网络错误
    if (response.status === 0 || !navigator.onLine) {
      errorMessage = `无法连接到服务器，请检查：\n1. 后端服务是否已启动\n2. API地址是否正确 (当前: ${getApiBase()})\n3. 网络连接是否正常`;
    }

    throw new Error(errorMessage);
  }

  return response.json();
}

export async function analyzeCode(code: string, inputs: Record<string, any> = {}): Promise<any> {
  const API_BASE = getApiBase();
  const aiApiKey = localStorage.getItem('aiApiKey');
  const aiProvider = localStorage.getItem('aiProvider') || 'openai';
  const aiModel = localStorage.getItem('aiModel') || 'gpt-4';

  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (aiApiKey) {
    headers['X-AI-Provider'] = aiProvider;
    headers['X-AI-Model'] = aiModel;
    headers['X-AI-API-Key'] = aiApiKey;
  }

  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ code, inputs }),
    });
    return handleApiResponse(response, '代码分析');
  } catch (e: any) {
    // 处理网络错误
    if (e.name === 'TypeError' && e.message.includes('Failed to fetch')) {
      throw new Error(`无法连接到服务器，请检查：\n1. 后端服务是否已启动 (访问 http://localhost:8000/health)\n2. API地址是否正确 (当前: ${API_BASE})\n3. 网络连接是否正常`);
    }
    throw e;
  }
}

export async function generateCourse(code: string, inputs: Record<string, any> = {}): Promise<any> {
  const API_BASE = getApiBase();
  const aiApiKey = localStorage.getItem('aiApiKey');
  const aiProvider = localStorage.getItem('aiProvider') || 'openai';
  const aiModel = localStorage.getItem('aiModel') || 'gpt-4';

  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (aiApiKey) {
    headers['X-AI-Provider'] = aiProvider;
    headers['X-AI-Model'] = aiModel;
    headers['X-AI-API-Key'] = aiApiKey;
  }

  try {
    const response = await fetch(`${API_BASE}/generate-course`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ code, inputs }),
    });
    return handleApiResponse(response, '课程生成');
  } catch (e: any) {
    if (e.name === 'TypeError' && e.message.includes('Failed to fetch')) {
      throw new Error(`无法连接到服务器，请检查：\n1. 后端服务是否已启动\n2. API地址是否正确 (当前: ${API_BASE})\n3. 网络连接是否正常`);
    }
    throw e;
  }
}

export async function comparePaths(code: string, inputsList: Record<string, any>[]): Promise<any> {
  const API_BASE = getApiBase();
  const aiApiKey = localStorage.getItem('aiApiKey');
  const aiProvider = localStorage.getItem('aiProvider') || 'openai';
  const aiModel = localStorage.getItem('aiModel') || 'gpt-4';

  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (aiApiKey) {
    headers['X-AI-Provider'] = aiProvider;
    headers['X-AI-Model'] = aiModel;
    headers['X-AI-API-Key'] = aiApiKey;
  }

  try {
    const response = await fetch(`${API_BASE}/compare-paths`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ code, inputs_list: inputsList }),
    });
    return handleApiResponse(response, '路径对比');
  } catch (e: any) {
    if (e.name === 'TypeError' && e.message.includes('Failed to fetch')) {
      throw new Error(`无法连接到服务器，请检查：\n1. 后端服务是否已启动\n2. API地址是否正确 (当前: ${API_BASE})\n3. 网络连接是否正常`);
    }
    throw e;
  }
}
