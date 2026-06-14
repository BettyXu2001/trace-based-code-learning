// Get API base URL from localStorage or environment variable
const getApiBase = () => {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
};

// 统一的请求配置
const getRequestConfig = () => ({
  headers: { 'Content-Type': 'application/json' },
});

// 统一的网络错误提示
const getNetworkErrorMessage = (apiBase: string) =>
  `无法连接到服务器，请检查：\n1. 后端服务是否已启动\n2. API地址是否正确 (当前: ${apiBase})\n3. 网络连接是否正常`;

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

    throw new Error(errorMessage);
  }

  return response.json();
}

// 通用的 API 请求函数，统一处理网络错误
async function apiRequest<T>(
  endpoint: string,
  actionName: string,
  body: any
): Promise<T> {
  const API_BASE = getApiBase();
  const config = getRequestConfig();

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      ...config,
      body: JSON.stringify(body),
    });
    return handleApiResponse<T>(response, actionName);
  } catch (e: any) {
    // 处理网络错误
    if (e.name === 'TypeError' && e.message.includes('Failed to fetch')) {
      throw new Error(getNetworkErrorMessage(API_BASE));
    }
    throw e;
  }
}

export async function analyzeCode(code: string, inputs: Record<string, any> = {}): Promise<any> {
  return apiRequest('/analyze', '代码分析', { code, inputs });
}

export async function generateCourse(code: string, inputs: Record<string, any> = {}): Promise<any> {
  return apiRequest('/generate-course', '课程生成', { code, inputs });
}

export async function comparePaths(code: string, inputsList: Record<string, any>[]): Promise<any> {
  return apiRequest('/compare-paths', '路径对比', { code, inputs_list: inputsList });
}
