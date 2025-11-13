import React, { useState, useEffect } from 'react';

function RegulationPipeline() {
  const [editedRegs, setEditedRegs] = useState([]);

  useEffect(() => {
    fetch("regulations.json")
      .then(res => res.json())
      .then(data => setEditedRegs(data));
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Regulation Review Console</h1>
      {editedRegs.map((reg, index) => (
        <div key={index} style={{ marginBottom: '2rem', borderBottom: '1px solid #ccc' }}>
          <h2>{reg.bill} ({reg.jurisdiction})</h2>
          <p><strong>Docket:</strong> {reg.docket}</p>
          <p><strong>Status:</strong> {reg.status}</p>
          <p><strong>Confidence:</strong> {reg.confidence}</p>
          <p><strong>Last Updated:</strong> {reg.lastUpdated}</p>
          <p><strong>Source:</strong> <a href={reg.sourceUrls[0]} target="_blank" rel="noreferrer">{reg.sourceUrls[0]}</a></p>

          <h3>Extracted Fields</h3>
          {Object.entries(reg.fields).map(([field, value]) => (
            <div key={field}>
              <p><strong>{field}:</strong> {value.answer} <em>(confidence: {value.confidence})</em></p>
            </div>
          ))}

          <h3>Tags</h3>
          <ul>
            {reg.tags.map(([tag, category], i) => (
              <li key={i}>{tag} <em>({category})</em></li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default RegulationPipeline;

