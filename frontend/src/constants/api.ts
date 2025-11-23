"""Frontend constants and configuration."""
export const API_BASE_URL = process.env.VITE_API_URL || "http://localhost:8000";

export const INTERVIEW_TYPES = {
  CODING: "coding",
  HR: "hr",
  SALES: "sales",
  MEMORY: "memory",
};

export const ROLES = [
  "Software Engineer",
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "Data Scientist",
  "DevOps Engineer",
];
