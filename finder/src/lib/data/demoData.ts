import type { Employee } from '../types.js';

const firstNames = [
  'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Mary',
  'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Nancy',
  'Lisa', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle', 'Laura',
  'Sarah', 'Kimberly', 'Deborah', 'Dorothy', 'Amy', 'Angela', 'Ashley', 'Brenda', 'Emma', 'Olivia',
  'Ava', 'Isabella', 'Sophia', 'Charlotte', 'Mia', 'Amelia', 'Harper', 'Evelyn', 'Abigail', 'Emily',
  'Daniel', 'Christopher', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua',
  'Kenneth', 'Kevin', 'Brian', 'George', 'Timothy', 'Ronald', 'Jason', 'Edward', 'Jeffrey', 'Ryan'
];

const lastNames = [
  'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
  'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
  'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
  'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts'
];

const positions = [
  'Software Engineer', 'Senior Software Engineer', 'Lead Software Engineer', 'Principal Engineer',
  'Product Manager', 'Senior Product Manager', 'Project Manager', 'Engineering Manager',
  'Data Scientist', 'Senior Data Scientist', 'Data Analyst', 'Business Analyst',
  'UX Designer', 'UI Designer', 'Senior Designer', 'Design Lead',
  'Marketing Manager', 'Sales Manager', 'Account Executive', 'Customer Success Manager',
  'DevOps Engineer', 'Site Reliability Engineer', 'Security Engineer', 'Quality Assurance Engineer',
  'Technical Writer', 'Scrum Master', 'Operations Manager', 'HR Manager',
  'Financial Analyst', 'Accountant', 'Legal Counsel', 'Executive Assistant'
];

const departments = [
  'Engineering', 'Product', 'Design', 'Marketing', 'Sales', 'Customer Success',
  'Operations', 'Human Resources', 'Finance', 'Legal', 'Data & Analytics', 'Security'
];

function getRandomElement<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

function getRandomDate(start: Date, end: Date): Date {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

function generateEmployee(id: number): Employee {
  const firstName = getRandomElement(firstNames);
  const lastName = getRandomElement(lastNames);
  const name = `${firstName} ${lastName}`;
  const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@company.com`;
  const position = getRandomElement(positions);
  const department = getRandomElement(departments);

  // Salary based on position level
  const baseSalary = position.includes('Senior') ? 95000 :
                    position.includes('Lead') || position.includes('Principal') ? 130000 :
                    position.includes('Manager') ? 110000 : 75000;
  const salary = baseSalary + Math.floor(Math.random() * 50000);

  const startDate = getRandomDate(new Date('2020-01-01'), new Date());
  const isActive = Math.random() > 0.1; // 90% active
  const performanceScore = Math.round((Math.random() * 4 + 1) * 10) / 10; // 1.0 to 5.0
  const projectsCompleted = Math.floor(Math.random() * 50) + 1;

  return {
    id,
    name,
    email,
    position,
    department,
    salary,
    startDate,
    isActive,
    performanceScore,
    projectsCompleted
  };
}

export function generateDemoData(count: number = 1500): Employee[] {
  return Array.from({ length: count }, (_, i) => generateEmployee(i + 1));
}

// Pre-generate data for consistent performance
export const demoEmployees = generateDemoData(1500);
