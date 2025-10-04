  // Frontend-only delete handler
  const handleDelete = (id) => {
    setInvoices((prev) => prev.filter((invoice) => invoice.id !== id));
  };
// src/App.jsx (Final Version with Image Display)
import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchInvoices = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/invoices/');
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setInvoices(data);
    } catch (error) {
      setError('Failed to fetch invoices.');
      console.error('Fetch error:', error);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }
    setIsLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/extract_invoice/', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to extract invoice.');
      }
      // Refresh the list AFTER the new data is posted
      fetchInvoices();
    } catch (error) {
      setError(error.message);
      console.error('Upload error:', error);
    } finally {
      setIsLoading(false);
      setSelectedFile(null);
      event.target.reset();
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="title">📄 VisionFlow Extractor</h1>
        <p className="subtitle">Upload an invoice image to extract data using AI.</p>
      </header>
      <main className="app-main">
        <form className="upload-form" onSubmit={handleSubmit}>
          <input className="file-input" type="file" onChange={handleFileChange} accept="image/*" />
          <button className="primary-btn" type="submit" disabled={isLoading || !selectedFile}>
            {isLoading ? 'Processing...' : 'Extract Data'}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}
        <section className="invoice-table-section">
          <h2>Processed Invoices</h2>
          <div className="table-wrapper">
            <table className="invoice-table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Invoice Date</th>
                  <th>Due Date</th>
                  <th>Total Amount</th>
                  <th>Proof</th>
                  <td>
                    <button className="delete-btn" type="button" onClick={() => handleDelete(invoice.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>{invoice.vendor_name}</td>
                    <td>{invoice.invoice_date}</td>
                    <td>{invoice.due_date}</td>
                    <td>${invoice.total_amount ? invoice.total_amount.toFixed(2) : 'N/A'}</td>
                    <thead>
                      <tr>
                        <th>Vendor</th>
                        <th>Invoice Date</th>
                        <th>Due Date</th>
                        <th>Total Amount</th>
                        <th>Proof</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
      <footer className="app-footer">
        <span>© {new Date().getFullYear()} VisionFlow. All rights reserved.</span>
      </footer>
    </div>
  );
}

export default App;