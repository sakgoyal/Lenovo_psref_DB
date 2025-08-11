export interface Employee {
  id: number;
  name: string;
  email: string;
  position: string;
  department: string;
  salary: number;
  startDate: Date;
  isActive: boolean;
  performanceScore: number;
  projectsCompleted: number;
}

export interface TableState {
  loading: boolean;
  pageIndex: number;
  pageSize: number;
  globalFilter: string;
  columnFilters: Record<string, any>;
  sorting: Array<{ id: string; desc: boolean }>;
  columnVisibility: Record<string, boolean>;
}

export interface PaginationInfo {
  pageIndex: number;
  pageSize: number;
  pageCount: number;
  total: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}