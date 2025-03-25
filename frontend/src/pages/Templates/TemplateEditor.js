import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Divider,
  Tabs,
  Tab,
  Card,
  CardContent
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
  Preview as PreviewIcon
} from '@mui/icons-material';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`template-tabpanel-${index}`}
      aria-labelledby={`template-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function TemplateEditor() {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const isNewTemplate = !templateId;
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [template, setTemplate] = useState({
    name: '',
    description: '',
    type: '',
    content: '',
    variables: {}
  });
  const [tabValue, setTabValue] = useState(0);
  const [previewData, setPreviewData] = useState(null);

  useEffect(() => {
    const fetchTemplate = async () => {
      if (isNewTemplate) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // Fetch template data
        const response = await axios.get(`/api/templates/${templateId}`);
        setTemplate(response.data);
        
      } catch (err) {
        console.error('Error fetching template:', err);
        setError(err.response?.data?.detail || 'Failed to load template. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTemplate();
  }, [templateId, isNewTemplate]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    
    // Generate preview when switching to preview tab
    if (newValue === 1) {
      generatePreview();
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTemplate(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleVariableChange = (variableName, value) => {
    setTemplate(prev => ({
      ...prev,
      variables: {
        ...prev.variables,
        [variableName]: value
      }
    }));
  };

  const generatePreview = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Generate preview
      const response = await axios.post('/api/templates/preview', {
        template_type: template.type,
        content: template.content,
        variables: template.variables
      });
      
      setPreviewData(response.data);
      
    } catch (err) {
      console.error('Error generating preview:', err);
      setError(err.response?.data?.detail || 'Failed to generate preview. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    // Validate form
    if (!template.name || !template.type || !template.content) {
      setError('Please fill in all required fields.');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      
      if (isNewTemplate) {
        // Create new template
        await axios.post('/api/templates', template);
      } else {
        // Update existing template
        await axios.put(`/api/templates/${templateId}`, template);
      }
      
      // Navigate back to templates list
      navigate('/templates');
      
    } catch (err) {
      console.error('Error saving template:', err);
      setError(err.response?.data?.detail || 'Failed to save template. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const getVariableFields = () => {
    switch (template.type) {
      case 'attendance_record':
        return [
          { name: 'student_name', label: 'Student Name' },
          { name: 'tutor_name', label: 'Tutor Name' },
          { name: 'month', label: 'Month' },
          { name: 'year', label: 'Year' }
        ];
      case 'progress_report':
        return [
          { name: 'student_name', label: 'Student Name' },
          { name: 'tutor_name', label: 'Tutor Name' },
          { name: 'period', label: 'Period' },
          { name: 'subject', label: 'Subject' }
        ];
      case 'invoice':
        return [
          { name: 'client_name', label: 'Client Name' },
          { name: 'invoice_number', label: 'Invoice Number' },
          { name: 'date', label: 'Date' },
          { name: 'amount', label: 'Amount' }
        ];
      case 'service_log':
        return [
          { name: 'student_name', label: 'Student Name' },
          { name: 'service_type', label: 'Service Type' },
          { name: 'date_range', label: 'Date Range' }
        ];
      default:
        return [];
    }
  };

  if (loading && !template.name) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          {isNewTemplate ? 'Create Template' : 'Edit Template'}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<CancelIcon />}
            onClick={() => navigate('/templates')}
            sx={{ mr: 2 }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Template'}
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Edit Template" />
          <Tab label="Preview" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                label="Template Name"
                name="name"
                value={template.name}
                onChange={handleInputChange}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal" required>
                <InputLabel>Template Type</InputLabel>
                <Select
                  name="type"
                  value={template.type}
                  onChange={handleInputChange}
                  label="Template Type"
                >
                  <MenuItem value="">Select Type</MenuItem>
                  <MenuItem value="attendance_record">Attendance Record</MenuItem>
                  <MenuItem value="progress_report">Progress Report</MenuItem>
                  <MenuItem value="invoice">Invoice</MenuItem>
                  <MenuItem value="service_log">Service Log</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={template.description}
                onChange={handleInputChange}
                margin="normal"
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Template Content"
                name="content"
                value={template.content}
                onChange={handleInputChange}
                margin="normal"
                multiline
                rows={10}
                placeholder="Enter your template content here. Use {{variable_name}} for dynamic content."
                helperText="Use {{variable_name}} syntax for dynamic content (e.g., {{student_name}})."
              />
            </Grid>
          </Grid>

          {template.type && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Test Variables
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Enter test values for variables to use in the preview.
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                {getVariableFields().map((field) => (
                  <Grid item xs={12} sm={6} md={3} key={field.name}>
                    <TextField
                      fullWidth
                      label={field.label}
                      value={template.variables[field.name] || ''}
                      onChange={(e) => handleVariableChange(field.name, e.target.value)}
                      margin="normal"
                    />
                  </Grid>
                ))}
              </Grid>
              
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<PreviewIcon />}
                  onClick={generatePreview}
                >
                  Generate Preview
                </Button>
              </Box>
            </Box>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : previewData ? (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Preview
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Box className="template-preview" dangerouslySetInnerHTML={{ __html: previewData.html }} />
              </CardContent>
            </Card>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <PreviewIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No Preview Available
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Fill in the template content and test variables, then click "Generate Preview".
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PreviewIcon />}
                onClick={() => {
                  generatePreview();
                }}
              >
                Generate Preview
              </Button>
            </Box>
          )}
        </TabPanel>
      </Paper>
    </Box>
  );
}

export default TemplateEditor;
