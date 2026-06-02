import React, { useState } from "react";
import "./index.css";

function App() {

  // ✅ STATES (UNCHANGED)
  const [repoUrl, setRepoUrl] = useState("");
  const [message, setMessage] = useState("");
  const [functions, setFunctions] = useState([]);
  const [search, setSearch] = useState("");
  const [aiDoc, setAiDoc] = useState("");
  const [zipFile, setZipFile] = useState(null);
  const [folderFiles, setFolderFiles] = useState([]);

  const [loadingClone, setLoadingClone] = useState(false);
  const [loadingRead, setLoadingRead] = useState(false);
  const [loadingDoc, setLoadingDoc] = useState(false);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);

  // ✅ CLONE
  const cloneRepo = async () => {
    setLoadingClone(true);
    try {
      const res = await fetch("http://127.0.0.1:5001/clone-repo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repoUrl })
      });
      const data = await res.json();
      setMessage(data.message);
    } catch {
      setMessage("Error cloning ❌");
    }
    setLoadingClone(false);
  };

  // ✅ READ
  const readFile = async () => {
    setLoadingRead(true);
    try {
      const res = await fetch("http://127.0.0.1:5001/read-file");
      const data = await res.json();
      setMessage(data.content || "No README ❌");
    } catch {
      setMessage("Error ❌");
    }
    setLoadingRead(false);
  };

  // ✅ DOC
  const generateDoc = async () => {
    setLoadingDoc(true);
    try {
      const res = await fetch("http://127.0.0.1:5001/generate-doc");
      const data = await res.json();
      setMessage(data.documentation);
    } catch {
      setMessage("Doc error ❌");
    }
    setLoadingDoc(false);
  };

  // ANALYZE
  const analyzeCode = async () => {
    setLoadingAnalyze(true);
    try {
      const res = await fetch("http://127.0.0.1:5001/parse-repo");
      const data = await res.json();
      setFunctions(data.functions || []);
    } catch {
      setFunctions([]);
    }
    setLoadingAnalyze(false);
  };

  // AI
  const generateAIDoc = async () => {
    setLoadingAI(true);
    try {
      const res = await fetch("http://127.0.0.1:5001/ai-doc");
      const data = await res.json();
      setAiDoc(data.aiDoc || "AI error ❌");
    } catch {
      setAiDoc("AI error ❌");
    }
    setLoadingAI(false);
  };

  // ✅ ZIP
  const uploadZip = async () => {
    const formData = new FormData();
    formData.append("file", zipFile);

    const res = await fetch("http://127.0.0.1:5001/upload-zip", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setMessage(data.message);
  };

  // ✅ FOLDER
  const uploadFolder = async () => {
    const formData = new FormData();
    for (let i = 0; i < folderFiles.length; i++) {
      formData.append("files", folderFiles[i]);
    }

    const res = await fetch("http://127.0.0.1:5001/upload-folder", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setMessage(data.message);
  };

  // ✅ PDF
  const downloadPDF = async () => {
    const res = await fetch("http://127.0.0.1:5001/download-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: aiDoc })
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "doc.pdf";
    a.click();
  };

  // ✅ WORD
  const downloadWord = async () => {
    const res = await fetch("http://127.0.0.1:5001/download-word", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: aiDoc })
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "doc.docx";
    a.click();
  };

// UI
return (
  <div className="app-container">

    <h1 className="title">AI-Powered Code Document Generator</h1>

    {/* REPO INPUT */}
    <div className="section">
      <input
        className="input"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        placeholder="Enter GitHub Repository URL"
      />
      <button className="btn blue" onClick={cloneRepo}>Clone</button>
      {/* Loading Message */}
      {(loadingClone || loadingRead || loadingDoc || loadingAnalyze|| loadingAI) && (
        <p style={styles.loadingText}>
          ⏳ Processing... Please wait
        </p>
      )}
    </div>

    {/* ✅ UPLOAD */}
    <div className="upload-section">

      {/* ZIP Upload */}
      <div className="upload-box">
        <input type="file" accept=".zip" onChange={(e)=>setZipFile(e.target.files[0])}/>
        <button className="btn dark" onClick={uploadZip}>Upload ZIP</button>
      </div>

      {/* FILE Upload */}
      <div className="upload-box">
        <input type="file" multiple onChange={(e)=>setFolderFiles(e.target.files)}/>
        <button className="btn dark" onClick={uploadFolder}>Upload Files</button>
      </div>

      {/* FOLDER */}
      <div className="upload-box">
        <input type="file" webkitdirectory="true" multiple onChange={(e)=>setFolderFiles(e.target.files)}/>
        <button className="btn dark" onClick={uploadFolder}>Upload Folder</button>
      </div>
    </div>

    {/* ACTION BUTTONS */}
    <div className="actions">
      <button className="btn green" onClick={readFile}>Read README</button>
      <button className="btn red" onClick={generateDoc}>Generate Documentation</button>
      <button className="btn purple" onClick={analyzeCode}>Analyze Code</button>
      <button className="btn orange" onClick={generateAIDoc}>AI Generate</button>
    </div>

    {/* MESSAGE */}
    {message && (
      <div className="box">
        <pre className="doc">{message}</pre>
      </div>
    )}


    {/* FUNCTIONS */}
    {functions.length > 0 && (
      <div className="box">
        <h3>Functions ({functions.length})</h3>

        <input
          className="search"
          placeholder="Search..."
          onChange={(e)=>setSearch(e.target.value)}
        />

        <ul className="grid">
          {functions
            .filter(f => f.toLowerCase().includes(search.toLowerCase()))
            .map((f,i)=><li key={i}>🔹 {f}</li>)
          }
        </ul>
      </div>
    )}

    {/* ✅ AI OUTPUT */}
    {aiDoc && (
      <div className="box">
        <h3>AI Documentation</h3>
        <div className="doc">{aiDoc}</div>
        <div className="download-section">
          <button className="btn download-pdf" onClick={downloadPDF}>
            PDF
          </button>
          <button className="btn download-word" onClick={downloadWord}>
            Word
          </button>
        </div>
      </div>
    )}

  </div>
);

}

export default App;
const styles = {
  page: {
    minHeight: "100vh",
    padding: "40px",
    background: "linear-gradient(135deg,#f7a8c4,#fddde6)",
    textAlign: "center"
  },
  title: { color: "#1c2c5b" },
  section: { display:"flex", justifyContent:"center", gap:"10px", margin:"10px", flexWrap:"wrap" },
  input: { padding:"10px", borderRadius:"8px", border:"none", width:"300px" },
  actions: { display:"flex", justifyContent:"center", gap:"10px", margin:"20px" },
  blueBtn:{background:"#007bff",color:"#fff",padding:"10px",border:"none",borderRadius:"6px"},
  greenBtn:{background:"#28a745",color:"#fff",padding:"10px",border:"none",borderRadius:"6px"},
  redBtn:{background:"#dc3545",color:"#fff",padding:"10px",border:"none",borderRadius:"6px"},
  purpleBtn:{background:"#6f42c1",color:"#fff",padding:"10px",border:"none",borderRadius:"6px"},
  orangeBtn:{background:"#fd7e14",color:"#fff",padding:"10px",border:"none",borderRadius:"6px"},
  darkBtn:{background:"#343a40",color:"#fff",padding:"10px",border:"none",borderRadius:"6px"},
  message:{marginTop:"10px"},
  loading:{color:"#fff"},
  box:{marginTop:"20px",padding:"15px",background:"rgba(255,255,255,0.6)",borderRadius:"10px"},
  search:{width:"100%",padding:"8px"},
  grid:{display:"grid",gridTemplateColumns:"repeat(3,1fr)"},
  doc:{whiteSpace:"pre-wrap"},
  row:{display:"flex",justifyContent:"center",gap:"10px"},
  downloadBtn:{background:"#17a2b8",color:"#fff",padding:"8px"},
  downloadBtn2:{background:"#965a99",color:"#fff",padding:"8px"}
};
