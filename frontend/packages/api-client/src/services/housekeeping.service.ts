import ApiClient from '../client';

export type TaskType = 'cleaning' | 'maintenance' | 'restocking' | 'inspection' | 'turndown';
export type TaskStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'verified' | 'delayed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: string;
  reference: string;
  task_type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  venue_id: string;
  room_number?: string;
  floor_number?: number;
  description?: string;
  assigned_staff_id?: string;
  assigned_staff_name?: string;
  is_vip: boolean;
  scheduled_start?: string;
  scheduled_end?: string;
  actual_start?: string;
  actual_end?: string;
  delay_reason?: string;
  completion_notes?: string;
  quality_score?: number;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TaskCreate {
  task_type: TaskType;
  priority?: TaskPriority;
  venue_id: string;
  room_number?: string;
  floor_number?: number;
  description?: string;
  is_vip?: boolean;
  scheduled_start?: string;
  scheduled_end?: string;
}

export interface TaskCompletion {
  notes?: string;
  issues_found?: string[];
  supplies_used?: Record<string, number>;
}

export interface TaskFilters {
  task_types?: TaskType[];
  statuses?: TaskStatus[];
  priorities?: TaskPriority[];
  venue_id?: string;
  floor_number?: number;
  assigned_staff_id?: string;
  is_vip?: boolean;
  scheduled_date_from?: string;
  scheduled_date_to?: string;
  page?: number;
  page_size?: number;
}

export class HousekeepingService {
  constructor(private client: ApiClient) {}

  async listTasks(filters?: TaskFilters): Promise<TaskListResponse> {
    return this.client.get('/v1/tasks', { params: filters });
  }

  async getTask(taskId: string): Promise<Task> {
    return this.client.get(`/v1/tasks/${taskId}`);
  }

  async getTaskByReference(reference: string): Promise<Task> {
    return this.client.get(`/v1/tasks/reference/${reference}`);
  }

  async createTask(data: TaskCreate): Promise<Task> {
    return this.client.post('/v1/tasks', data);
  }

  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    return this.client.patch(`/v1/tasks/${taskId}`, updates);
  }

  async assignTask(taskId: string, staffId: string): Promise<Task> {
    return this.client.post(`/v1/tasks/${taskId}/assign`, { staff_id: staffId });
  }

  async startTask(taskId: string): Promise<Task> {
    return this.client.post(`/v1/tasks/${taskId}/start`);
  }

  async completeTask(taskId: string, completion?: TaskCompletion): Promise<Task> {
    return this.client.post(`/v1/tasks/${taskId}/complete`, completion || {});
  }

  async markDelayed(taskId: string, reason: string): Promise<Task> {
    return this.client.post(`/v1/tasks/${taskId}/delay`, null, {
      params: { reason },
    });
  }

  async verifyTask(taskId: string, verifiedBy: string, qualityScore?: number): Promise<Task> {
    return this.client.post(`/v1/tasks/${taskId}/verify`, null, {
      params: { verified_by: verifiedBy, quality_score: qualityScore },
    });
  }

  async getPendingTasks(limit = 50): Promise<Task[]> {
    return this.client.get('/v1/tasks/pending', { params: { limit } });
  }

  async getOverdueTasks(): Promise<Task[]> {
    return this.client.get('/v1/tasks/overdue');
  }

  async autoAssignTasks(limit = 10): Promise<{ task_id: string; staff_id: string }[]> {
    return this.client.post('/v1/tasks/auto-assign', null, { params: { limit } });
  }
}
