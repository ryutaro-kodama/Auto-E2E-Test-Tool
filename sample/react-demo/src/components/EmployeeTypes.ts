export type Gender = 'Male' | 'Female' | 'Other';

export interface Employee {
    id: string;
    name: string;
    gender: Gender;
    dateOfBirth: string; // ISO format: YYYY-MM-DD
}

export interface EmployeeSearchParams {
    name?: string;
    gender?: string;
    dateOfBirth?: string;
}
