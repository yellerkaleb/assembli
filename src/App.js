import React, { useState } from 'react';

export default function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

const handleUpload = async () => {
  setLoading(true);
  try {
    const uploads = files.map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
    });
    await Promise.all(uploads);
    await handleProcess();
  } catch (err) {
    console.error('Upload error:', err);
    alert('Upload failed: ' + err.message);
  }
  setLoading(false);
};


  const handleProcess = async () => {
    setLoading(true);
    const res = await fetch('http://localhost:5000/process-folder');
    const data = await res.json();
    setResults(data);
    setLoading(false);
  };

  //const getImageSrc = (filename) => `/uploads/${filename}`;
  const getImageSrc = (filename) => `http://localhost:5000/uploads/${filename}`;

  const styles={
      imgThumbnail:{width:'100px',height:'70px',objectFit:"cover"},
      btn:{minWidth:'10rem',margin:'1rem'}
    }
  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h1 className="text-xl font-bold mb-4">📤 Upload Images for Tagging</h1>

      <input type="file" multiple accept="image/*" onChange={handleFileChange} className="mb-2 p-6" style={styles.btn} />

      <div className="space-x-2 mt-2">
        <button onClick={handleUpload} className="px-4 py-2 bg-blue-500 text-white rounded p-6" style={styles.btn}>
          Process
        </button>
      </div>

      {loading && <p className="mt-4">⏳ Processing...</p>}

      {results.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">🧾 Processed Results</h2>
          <table className="table-auto w-full border">
            <thead>
              <tr className="bg-gray-100">
                <th className="border px-2 py-1">Image</th>
                <th className="border px-2 py-1">Tag</th>
                <th className="border px-2 py-1">Filename</th>
                <th className="border px-2 py-1">Error</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, idx) => (
                <tr key={idx}>
                  <td className="border px-2 py-1">
                    <img
                      style={styles.imgThumbnail}
                      src={getImageSrc(r.filename)}
                      alt={r.filename}
                      className="w-16 h-16 object-cover rounded"
                      onError={(e) => (e.target.style.display = 'none')}
                    />
                  </td>
                  <td className="border px-2 py-1">{r.tag || '-'}</td>
                  <td className="border px-2 py-1 w-1" >{r.filename}</td>
                  <td className="border px-2 py-1 text-red-500">{r.error || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
