import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import io from 'socket.io-client';
import '../components/visualizeStyle.css';
import Navbar from './Navbar';

// Initialize Socket.IO client
const socket = io('http://localhost:5000', { transports: ['websocket'] });

const POINTS_PER_GRAPH = 300; // Increase for better ECG visualization

const Visualize = () => {
  const [isCollecting, setIsCollecting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [ecgData, setEcgData] = useState([]);
  const [showGraph, setShowGraph] = useState(false);
  const [summary, setSummary] = useState(null); // State to store ECG summary

  // Fetch ECG data from CSV and plot it
  const loadAndPlotData = async () => {
    try {
      const response = await fetch('http://localhost:5000/ecg_data.csv');
      const csvText = await response.text();

      const rows = csvText.split('\n').slice(1); // Skip header
      const data = rows
        .filter((row) => row.trim() !== '') // Remove empty rows
        .map((row) => {
          const [time, ecg] = row.split(',');
          return {
            time: parseFloat(time),
            ecg: parseFloat(ecg),
          };
        });

      setEcgData(data);
      setShowGraph(true);
    } catch (error) {
      console.error('Error loading CSV data:', error);
    }
  };

  // Organize data into continuous chunks for sub-graphs
  const getGraphSegments = () => {
    let segments = [];
    for (let i = 0; i < ecgData.length; i += POINTS_PER_GRAPH) {
      let segment = ecgData.slice(i, i + POINTS_PER_GRAPH);
      if (segments.length > 0 && segment.length > 0) {
        segment.unshift(segments[segments.length - 1].slice(-1)[0]); // Maintain continuity
      }
      segments.push(segment);
    }
    return segments;
  };

  // Start ECG data collection
  const handleStart = () => {
    setIsCollecting(true);
    setIsLoading(true);
    setShowGraph(false);
    setEcgData([]);
    socket.emit('start_ecg');
  };

  // Stop ECG data collection
  const handleStop = () => {
    setIsCollecting(false);
    setIsLoading(false);
    socket.emit('stop_ecg');
  };

  // Visualize stored ECG dataset
  const handleVisualize = () => {
    loadAndPlotData();
  };

  // Clear the graph from frontend
  const handleClear = () => {
    setEcgData([]);
    setShowGraph(false);
    setSummary(null); // Clear summary when clearing the graph
  };

  // Fetch ECG summary from the backend
  const handleSummarize = async () => {
    try {
      const response = await fetch('http://localhost:5000/summarize_ecg');
      const data = await response.json();
      setSummary(data); // Store the ECG summary in state
    } catch (error) {
      console.error('Error fetching ECG summary:', error);
    }
  };

  // Render the summary as a table
  const renderSummaryTable = () => {
    if (!summary) return null;

    const { data } = summary;

    return (
      <table className="summary-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data).map(([key, value]) => (
            <tr key={key}>
              <td>{key.replace(/_/g, ' ')}</td> {/* Replace underscores with spaces */}
              <td>{typeof value === 'number' ? value.toFixed(2) : value}</td> {/* Format numbers to 2 decimal places */}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  // Auto-stop after 2 minutes
  useEffect(() => {
    if (isCollecting) {
      const timeout = setTimeout(() => {
        setIsCollecting(false);
        setIsLoading(false);
        socket.emit('stop_ecg');
        loadAndPlotData();
      }, 120000);

      return () => clearTimeout(timeout);
    }
  }, [isCollecting]);

  return (
    <div>
      <Navbar />
      <div className="Ecg">
        <h1 className="Ecg-h1">ECG Data Visualization</h1>
        <div className="button-container">
          <div className="left-buttons">
            <button className="ecg-button" onClick={handleStart} disabled={isCollecting || isLoading}>
              {isLoading ? 'Collecting...' : 'Start'}
            </button>
            <button className="ecg-button" onClick={handleStop} disabled={!isCollecting}>
              Stop
            </button>
          </div>
          <div className="center-buttons">
            <button className="ecg-button visualize" onClick={handleVisualize} disabled={isCollecting}>
              Visualize
            </button>
            <button className="ecg-button clear" onClick={handleClear}>
              Clear
            </button>
          </div>
          <div className="right-buttons">
            <button className="ecg-button summarize" onClick={handleSummarize}>
              Summarize
            </button>
          </div>
        </div>

        {isLoading && <div className="loader"></div>}

        {showGraph && (
          <div className="graph-stack">
            {getGraphSegments().map((segment, index) => (
              <div key={index} className="graph-container">
                <h3 className="graph-label">Segment {index + 1}</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={segment} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    {/* Background grid mimicking ECG paper */}
                    <CartesianGrid
                      strokeDasharray="1 4" /* Small box grid (1mm) */
                      stroke="rgba(255, 0, 0, 0.3)"
                    />
                    <CartesianGrid
                      strokeDasharray="6 24" /* Large box grid (5mm) */
                      stroke="rgba(255, 0, 0, 0.7)"
                    />

                    {/* X & Y Axes */}
                    <XAxis
                      dataKey="time"
                      type="number"
                      domain={['auto', 'auto']}
                      tickFormatter={(tick) => tick.toFixed(2)}
                      tickCount={10}
                    />
                    <YAxis
                      dataKey="ecg"
                      type="number"
                      domain={[100, 600]} // Adjust based on your ECG range
                      tickCount={5}
                    />

                    {/* Tooltip & Legends */}
                    <Tooltip />
                    <Legend />

                    {/* ECG Signal Line */}
                    <Line
                      type="monotone" /* Smooth ECG-like curve */
                      dataKey="ecg"
                      stroke="red"
                      strokeWidth={2}
                      dot={false} /* Removes dots from data points */
                      strokeLinejoin="round"
                      strokeLinecap="round"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ))}
          </div>
        )}

        {summary && (
          <div className="summary-container">
            <h3>ECG Summary</h3>
            {renderSummaryTable()}
          </div>
        )}
      </div>
    </div>
  );
};

export default Visualize;