// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

// Mock the recharts components
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
    BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
    PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
    Bar: () => <div data-testid="bar" />,
    Pie: () => <div data-testid="pie" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
    Cell: () => <div data-testid="cell" />
  };
});

// Define handlers for API mocking
const handlers = [
  // Auth endpoints
  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access_token: 'mock-token',
        token_type: 'bearer'
      })
    );
  }),
  
  rest.get('/api/auth/profile', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User',
        is_admin: false
      })
    );
  }),
  
  // Processing endpoints
  rest.get('/api/processing/stats', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        activeJobs: 3,
        completedJobs: 10,
        failedJobs: 2,
        totalDocuments: 15,
        processingStages: [
          { stage: 'File Upload', count: 1 },
          { stage: 'Data Extraction', count: 2 },
          { stage: 'Validation', count: 0 },
          { stage: 'Document Generation', count: 0 },
          { stage: 'PDF Conversion', count: 0 }
        ]
      })
    );
  }),
  
  rest.get('/api/processing/jobs', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          status: 'completed',
          created_at: '2023-01-01T12:00:00Z',
          current_stage: 'pdf_conversion'
        },
        {
          id: 2,
          status: 'processing',
          created_at: '2023-01-02T12:00:00Z',
          current_stage: 'data_extraction'
        },
        {
          id: 3,
          status: 'failed',
          created_at: '2023-01-03T12:00:00Z',
          current_stage: 'validation'
        }
      ])
    );
  }),
  
  // OCR endpoints
  rest.get('/api/ocr/extract-text/:fileId', (req, res, ctx) => {
    const { fileId } = req.params;
    return res(
      ctx.status(200),
      ctx.json({
        file_id: fileId,
        text: 'Sample extracted text from PDF document.',
        character_count: 38
      })
    );
  }),
  
  rest.get('/api/ocr/parse-payroll/:fileId', (req, res, ctx) => {
    const { fileId } = req.params;
    return res(
      ctx.status(200),
      ctx.json({
        file_id: fileId,
        payroll_data: {
          period: 'January 1-15, 2023',
          tutors: [
            {
              id: 'ABC123',
              name: 'John Doe',
              total_hours: 10.5,
              hourly_rate: 25.0,
              sessions: [
                {
                  date: '01/01/2023',
                  start_time: '9:00 AM',
                  end_time: '11:30 AM',
                  hours: 2.5
                }
              ]
            }
          ]
        }
      })
    );
  })
];

// Setup MSW server
const server = setupServer(...handlers);

// Start server before all tests
beforeAll(() => server.listen());

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Close server after all tests
afterAll(() => server.close());

// Mock console.error to avoid polluting test output
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (/Warning.*not wrapped in act/.test(args[0])) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
