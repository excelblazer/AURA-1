import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  CardHeader,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  FileCopy as FileCopyIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';

function Templates() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [deleteTemplate, setDeleteTemplate] = useState(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch templates
        const response = await axios.get('/api/templates');
        setTemplates(response.data);
        
      } catch (err) {
        console.error('Error fetching templates:', err);
        setError(err.response?.data?.detail || 'Failed to load templates. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  const handleDeleteClick = (template) => {
    setDeleteTemplate(template);
  };

  const handleDeleteCancel = () => {
    setDeleteTemplate(null);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTemplate) return;

    try {
      setLoading(true);
      
      // Delete template
      await axios.delete(`/api/templates/${deleteTemplate.id}`);
      
      // Update templates list
      setTemplates(templates.filter(t => t.id !== deleteTemplate.id));
      
      // Close dialog
      setDeleteTemplate(null);
      
    } catch (err) {
      console.error('Error deleting template:', err);
      setError(err.response?.data?.detail || 'Failed to delete template. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getTemplateTypeChip = (type) => {
    switch (type) {
      case 'attendance_record':
        return <Chip label="Attendance Record" color="primary" size="small" />;
      case 'progress_report':
        return <Chip label="Progress Report" color="secondary" size="small" />;
      case 'invoice':
        return <Chip label="Invoice" color="info" size="small" />;
      case 'service_log':
        return <Chip label="Service Log" color="success" size="small" />;
      default:
        return <Chip label={type} size="small" />;
    }
  };

  if (loading && templates.length === 0) {
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
          Templates
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => navigate('/templates/new')}
        >
          New Template
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Document Templates
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Manage your document templates for attendance records, progress reports, invoices, and service logs.
            </Typography>
            <Divider sx={{ mb: 3 }} />

            {templates.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <DescriptionIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  No Templates Found
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Get started by creating your first template.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/templates/new')}
                >
                  Create Template
                </Button>
              </Box>
            ) : (
              <Grid container spacing={3}>
                {templates.map((template) => (
                  <Grid item xs={12} sm={6} md={4} key={template.id}>
                    <Card>
                      <CardHeader
                        title={template.name}
                        subheader={`Created: ${new Date(template.created_at).toLocaleDateString()}`}
                        action={getTemplateTypeChip(template.type)}
                      />
                      <CardContent>
                        <Typography variant="body2" color="textSecondary">
                          {template.description || 'No description provided.'}
                        </Typography>
                        
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="textSecondary">
                            Last modified: {new Date(template.updated_at).toLocaleString()}
                          </Typography>
                        </Box>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          startIcon={<EditIcon />}
                          onClick={() => navigate(`/templates/edit/${template.id}`)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={() => handleDeleteClick(template)}
                        >
                          Delete
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deleteTemplate}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>
          Delete Template
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the template "{deleteTemplate?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Templates;
