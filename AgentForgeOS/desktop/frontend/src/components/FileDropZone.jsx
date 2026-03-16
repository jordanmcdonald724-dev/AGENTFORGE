import { useState, useRef } from 'react';
import { Upload, File, X, FileText, FileCode, Image, Music, Video } from 'lucide-react';
import { toast } from 'sonner';

const getFileIcon = (type) => {
  if (type.startsWith('image/')) return Image;
  if (type.startsWith('video/')) return Video;
  if (type.startsWith('audio/')) return Music;
  if (type.includes('text') || type.includes('json') || type.includes('xml')) return FileText;
  if (type.includes('javascript') || type.includes('python') || type.includes('code')) return FileCode;
  return File;
};

const FileDropZone = ({ onFilesAdded, children, className = '' }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    await processFiles(files);
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    await processFiles(files);
  };

  const processFiles = async (files) => {
    if (files.length === 0) return;

    const fileData = [];
    
    for (const file of files) {
      try {
        // Read file content
        const content = await readFileContent(file);
        
        fileData.push({
          name: file.name,
          type: file.type,
          size: file.size,
          content: content,
          file: file
        });

        toast.success(`Loaded: ${file.name}`);
      } catch (error) {
        toast.error(`Failed to load: ${file.name}`);
        console.error('File read error:', error);
      }
    }

    if (fileData.length > 0) {
      setUploadedFiles(prev => [...prev, ...fileData]);
      onFilesAdded(fileData);
    }
  };

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      // For images, read as Data URL
      if (file.type.startsWith('image/')) {
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      }
      // For text/code files, read as text
      else if (
        file.type.includes('text') ||
        file.type.includes('json') ||
        file.type.includes('javascript') ||
        file.type.includes('python') ||
        file.type.includes('xml') ||
        file.type.includes('html') ||
        file.type.includes('css') ||
        file.name.match(/\.(txt|md|js|py|jsx|tsx|ts|css|html|json|xml|yml|yaml|sh|bat)$/i)
      ) {
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsText(file);
      }
      // For binary files, read as base64
      else {
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      }
    });
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="relative">
      {/* Drag Overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-blue-500/10 border-2 border-blue-500 border-dashed rounded-lg backdrop-blur-sm">
          <div className="text-center">
            <Upload className="w-12 h-12 mx-auto mb-2 text-blue-400" />
            <p className="text-sm font-medium text-blue-400">Drop files here</p>
            <p className="text-xs text-zinc-400 mt-1">All file types supported</p>
          </div>
        </div>
      )}

      {/* Drop Zone */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative ${className}`}
      >
        {children}

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept="*/*"
        />
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-2 space-y-1">
          {uploadedFiles.map((file, index) => {
            const Icon = getFileIcon(file.type);
            return (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-sm"
              >
                <Icon className="w-4 h-4 text-zinc-400 flex-shrink-0" />
                <span className="flex-1 truncate text-zinc-300">{file.name}</span>
                <span className="text-xs text-zinc-500">{formatFileSize(file.size)}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 rounded hover:bg-zinc-700 transition-colors"
                >
                  <X className="w-3 h-3 text-zinc-400" />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default FileDropZone;
