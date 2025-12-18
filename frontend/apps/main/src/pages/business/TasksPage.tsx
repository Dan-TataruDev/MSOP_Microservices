import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ClipboardList, Clock, AlertTriangle, CheckCircle, Play, User, Filter } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import type { TaskStatus, TaskType, TaskPriority } from '@hospitality-platform/api-client';

const statusColors: Record<string, string> = {
  pending: 'bg-slate-100 text-slate-700',
  assigned: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-green-100 text-green-700',
  verified: 'bg-purple-100 text-purple-700',
  delayed: 'bg-red-100 text-red-700',
  cancelled: 'bg-slate-200 text-slate-500',
};

const priorityColors: Record<string, string> = {
  low: 'bg-slate-100 text-slate-600',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700',
};

const typeIcons: Record<string, string> = {
  cleaning: '🧹',
  maintenance: '🔧',
  restocking: '📦',
  inspection: '🔍',
  turndown: '🛏️',
};

export default function TasksPage() {
  const queryClient = useQueryClient();
  const { businessContext } = useAuthStore();
  const venueId = businessContext?.businessId;
  
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<TaskType | 'all'>('all');
  const [page, setPage] = useState(1);

  // Get tasks
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', venueId, statusFilter, typeFilter, page],
    queryFn: async () => {
      return await apiServices.housekeeping.listTasks({
        venue_id: venueId,
        statuses: statusFilter !== 'all' ? [statusFilter as TaskStatus] : undefined,
        task_types: typeFilter !== 'all' ? [typeFilter as TaskType] : undefined,
        page,
        page_size: 20,
      });
    },
  });

  // Get overdue tasks count
  const { data: overdueTasks } = useQuery({
    queryKey: ['overdue-tasks'],
    queryFn: () => apiServices.housekeeping.getOverdueTasks(),
  });

  // Get pending tasks count
  const { data: pendingTasks } = useQuery({
    queryKey: ['pending-tasks'],
    queryFn: () => apiServices.housekeeping.getPendingTasks(100),
  });

  const startMutation = useMutation({
    mutationFn: (taskId: string) => apiServices.housekeeping.startTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: (taskId: string) => apiServices.housekeeping.completeTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['pending-tasks'] });
    },
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Task Management</h1>
        <p className="text-slate-600">Manage housekeeping and maintenance tasks</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <ClipboardList className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-sm text-slate-600">Total Tasks</p>
            <p className="text-3xl font-bold text-slate-900">{tasks?.total || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Clock className="w-8 h-8 text-yellow-600" />
            </div>
            <p className="text-sm text-slate-600">Pending</p>
            <p className="text-3xl font-bold text-slate-900">{pendingTasks?.length || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <p className="text-sm text-slate-600">Overdue</p>
            <p className="text-3xl font-bold text-red-600">{overdueTasks?.length || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-sm text-slate-600">Completed Today</p>
            <p className="text-3xl font-bold text-green-600">
              {tasks?.tasks?.filter(t => t.status === 'completed').length || 0}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-500" />
              <span className="text-sm font-medium text-slate-700">Filters:</span>
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="px-3 py-1.5 border border-slate-300 rounded-lg text-sm"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="delayed">Delayed</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as any)}
              className="px-3 py-1.5 border border-slate-300 rounded-lg text-sm"
            >
              <option value="all">All Types</option>
              <option value="cleaning">Cleaning</option>
              <option value="maintenance">Maintenance</option>
              <option value="restocking">Restocking</option>
              <option value="inspection">Inspection</option>
              <option value="turndown">Turndown</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <Card>
        <CardHeader>
          <CardTitle>Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : tasks?.tasks && tasks.tasks.length > 0 ? (
            <div className="space-y-4">
              {tasks.tasks.map((task) => (
                <div key={task.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{typeIcons[task.task_type] || '📋'}</span>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-slate-900">
                            {task.reference}
                          </h4>
                          {task.is_vip && (
                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium">
                              VIP
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-slate-600 mb-2">
                          {task.task_type.charAt(0).toUpperCase() + task.task_type.slice(1)}
                          {task.room_number && ` • Room ${task.room_number}`}
                          {task.floor_number && ` • Floor ${task.floor_number}`}
                        </p>
                        {task.description && (
                          <p className="text-sm text-slate-500">{task.description}</p>
                        )}
                        {task.assigned_staff_name && (
                          <div className="flex items-center gap-1 mt-2 text-sm text-slate-600">
                            <User className="w-4 h-4" />
                            {task.assigned_staff_name}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <div className="flex gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[task.status]}`}>
                          {task.status.replace('_', ' ')}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${priorityColors[task.priority]}`}>
                          {task.priority}
                        </span>
                      </div>
                      {task.scheduled_start && (
                        <p className="text-xs text-slate-500">
                          Due: {new Date(task.scheduled_start).toLocaleString()}
                        </p>
                      )}
                      <div className="flex gap-2 mt-2">
                        {task.status === 'assigned' && (
                          <Button
                            size="sm"
                            onClick={() => startMutation.mutate(task.id)}
                            disabled={startMutation.isPending}
                            leftIcon={<Play className="w-4 h-4" />}
                          >
                            Start
                          </Button>
                        )}
                        {task.status === 'in_progress' && (
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => completeMutation.mutate(task.id)}
                            disabled={completeMutation.isPending}
                            leftIcon={<CheckCircle className="w-4 h-4" />}
                          >
                            Complete
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                  {task.delay_reason && (
                    <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                      <strong>Delay reason:</strong> {task.delay_reason}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <ClipboardList className="w-12 h-12 text-slate-200 mx-auto mb-3" />
              <p className="text-slate-500">No tasks found</p>
            </div>
          )}

          {/* Pagination */}
          {tasks && tasks.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <Button
                variant="outline"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="px-4 py-2 text-slate-600">
                Page {page} of {tasks.total_pages}
              </span>
              <Button
                variant="outline"
                onClick={() => setPage(p => p + 1)}
                disabled={page >= tasks.total_pages}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
