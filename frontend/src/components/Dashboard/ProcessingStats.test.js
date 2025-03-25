import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProcessingStats from './ProcessingStats';
import { processingAPI } from '../../services/api';

// Mock the API service
jest.mock('../../services/api', () => ({
  processingAPI: {
    getProcessingStats: jest.fn(),
    getJobs: jest.fn()
  }
}));

// Mock recharts components
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

describe('ProcessingStats Component', () => {
  const mockStats = {
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
  };

  const mockJobs = [
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
  ];

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup mock responses
    processingAPI.getProcessingStats.mockResolvedValue({ data: mockStats });
    processingAPI.getJobs.mockResolvedValue({ data: mockJobs });
  });

  test('renders loading state initially', () => {
    render(<ProcessingStats />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders stats cards after loading', async () => {
    render(<ProcessingStats />);
    
    // Wait for the data to load
    await waitFor(() => {
      expect(processingAPI.getProcessingStats).toHaveBeenCalledTimes(1);
      expect(processingAPI.getJobs).toHaveBeenCalledTimes(1);
    });
    
    // Check if stats cards are rendered
    expect(screen.getByText('3')).toBeInTheDocument(); // Active Jobs
    expect(screen.getByText('10')).toBeInTheDocument(); // Completed Jobs
    expect(screen.getByText('15')).toBeInTheDocument(); // Total Documents
  });

  test('renders charts after loading', async () => {
    render(<ProcessingStats />);
    
    // Wait for the data to load
    await waitFor(() => {
      expect(processingAPI.getProcessingStats).toHaveBeenCalledTimes(1);
    });
    
    // Check if charts are rendered
    expect(screen.getByText('Estimated Processing Time by Stage')).toBeInTheDocument();
    expect(screen.getByText('Processing Stages Distribution')).toBeInTheDocument();
    expect(screen.getAllByTestId('responsive-container')).toHaveLength(2);
  });

  test('renders recent jobs list after loading', async () => {
    render(<ProcessingStats />);
    
    // Wait for the data to load
    await waitFor(() => {
      expect(processingAPI.getJobs).toHaveBeenCalledTimes(1);
    });
    
    // Check if recent jobs are rendered
    expect(screen.getByText('Recent Processing Jobs')).toBeInTheDocument();
    expect(screen.getByText('Job #1')).toBeInTheDocument();
    expect(screen.getByText('Job #2')).toBeInTheDocument();
    expect(screen.getByText('Job #3')).toBeInTheDocument();
    
    // Check job status chips
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Processing')).toBeInTheDocument();
    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    // Setup mock to reject
    processingAPI.getProcessingStats.mockRejectedValue(new Error('API error'));
    processingAPI.getJobs.mockRejectedValue(new Error('API error'));
    
    render(<ProcessingStats />);
    
    // Wait for the error to be displayed
    await waitFor(() => {
      expect(screen.getByText('Failed to load processing statistics. Please try again.')).toBeInTheDocument();
    });
  });

  test('displays correct estimated time for processing jobs', async () => {
    render(<ProcessingStats />);
    
    // Wait for the data to load
    await waitFor(() => {
      expect(processingAPI.getJobs).toHaveBeenCalledTimes(1);
    });
    
    // Check estimated time for completed job
    expect(screen.getByText('Estimated Time: Finished')).toBeInTheDocument();
    
    // Check estimated time for processing job
    // The exact text will depend on the implementation, but it should contain "minutes"
    const estimatedTimeElements = screen.getAllByText(/Estimated Time:/);
    expect(estimatedTimeElements.length).toBeGreaterThan(1);
    
    // At least one of them should mention minutes for the processing job
    const processingTimeText = estimatedTimeElements.some(el => 
      el.textContent.includes('minutes') || el.textContent.includes('minute')
    );
    expect(processingTimeText).toBeTruthy();
  });
});
