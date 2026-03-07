import { useState, useMemo } from 'react';
import './AdminDashboard.css';

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


// Stub data simulating a backend API response
const STUB_EMPLOYEES: Employee[] = [
    { id: 'EMP-001', name: '山田 太郎', gender: 'Male', dateOfBirth: '1990-01-15' },
    { id: 'EMP-002', name: '佐藤 花子', gender: 'Female', dateOfBirth: '1995-05-20' },
    { id: 'EMP-003', name: '鈴木 一郎', gender: 'Male', dateOfBirth: '1985-11-03' },
    { id: 'EMP-004', name: '田中 裕子', gender: 'Female', dateOfBirth: '1992-08-12' },
    { id: 'EMP-005', name: '伊藤 健太', gender: 'Male', dateOfBirth: '1998-03-25' },
];

export default function AdminDashboard() {
    const [searchParams, setSearchParams] = useState<EmployeeSearchParams>({
        name: '',
        gender: '',
        dateOfBirth: '',
    });

    const handleSearchChange = (field: keyof EmployeeSearchParams, value: string) => {
        setSearchParams(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const filteredEmployees = useMemo(() => {
        return STUB_EMPLOYEES.filter(emp => {
            const matchName = !searchParams.name || emp.name.toLowerCase().includes(searchParams.name.toLowerCase());
            const matchGender = !searchParams.gender || emp.gender === searchParams.gender;
            const matchDob = !searchParams.dateOfBirth || emp.dateOfBirth === searchParams.dateOfBirth;
            return matchName && matchGender && matchDob;
        });
    }, [searchParams]);

    return (
        <div className="admin-dashboard animate-fade-in">
            <div className="dashboard-header">
                <h1>Employee Directory</h1>
                <p className="subtitle">Manage and filter staff records seamlessly.</p>
            </div>

            <div className="search-panel">
                <h2 className="panel-title">Search Filters</h2>
                <div className="search-grid">
                    <div className="input-group">
                        <label htmlFor="name-filter">Name</label>
                        <input
                            id="name-filter"
                            type="text"
                            placeholder="Search by name..."
                            value={searchParams.name || ''}
                            onChange={(e) => handleSearchChange('name', e.target.value)}
                            className="styled-input"
                        />
                    </div>
                    <div className="input-group">
                        <label htmlFor="gender-filter">Gender</label>
                        <select
                            id="gender-filter"
                            value={searchParams.gender || ''}
                            onChange={(e) => handleSearchChange('gender', e.target.value)}
                            className="styled-input"
                        >
                            <option value="">All Genders</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div className="input-group">
                        <label htmlFor="dob-filter">Date of Birth</label>
                        <input
                            id="dob-filter"
                            type="date"
                            value={searchParams.dateOfBirth || ''}
                            onChange={(e) => handleSearchChange('dateOfBirth', e.target.value)}
                            className="styled-input"
                        />
                    </div>
                </div>
            </div>

            <div className="results-panel">
                <div className="results-header">
                    <h2>Results</h2>
                    <span className="badge">{filteredEmployees.length} found</span>
                </div>

                <div className="table-container">
                    <table className="styled-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Gender</th>
                                <th>Date of Birth</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredEmployees.length > 0 ? (
                                filteredEmployees.map(emp => (
                                    <tr key={emp.id} className="table-row">
                                        <td className="cell-id">{emp.id}</td>
                                        <td className="cell-name">{emp.name}</td>
                                        <td>
                                            <span className={`gender-badge ${emp.gender.toLowerCase()}`}>
                                                {emp.gender}
                                            </span>
                                        </td>
                                        <td>{emp.dateOfBirth}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={4} className="empty-state">
                                        <div className="empty-content">
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="empty-icon">
                                                <circle cx="11" cy="11" r="8"></circle>
                                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                            </svg>
                                            <p>No employees match your search criteria.</p>
                                            <button
                                                className="reset-btn"
                                                onClick={() => setSearchParams({ name: '', gender: '', dateOfBirth: '' })}
                                            >
                                                Clear Filters
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
