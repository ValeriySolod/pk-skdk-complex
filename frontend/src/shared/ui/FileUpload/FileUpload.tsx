import {
  useId,
  useRef,
  useState,
  type ChangeEvent,
  type KeyboardEvent,
  type ReactNode,
} from 'react';
import clsx from 'clsx';

import styles from './FileUpload.module.css';

export interface FileUploadProps {
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
  value?: File[];
  onChange?: (files: File[]) => void;
  className?: string;
  children?: ReactNode;
}

export function FileUpload({
  accept,
  multiple = false,
  disabled = false,
  value,
  onChange,
  className,
  children = 'Choose file',
}: FileUploadProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [internalFiles, setInternalFiles] = useState<File[]>([]);
  const selectedFiles = value ?? internalFiles;
  const hasSelectedFiles = selectedFiles.length > 0;

  function updateFiles(files: File[]) {
    if (disabled) {
      return;
    }

    if (value === undefined) {
      setInternalFiles(files);
    }

    onChange?.(files);
  }

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    updateFiles(Array.from(event.target.files ?? []));
    event.target.value = '';
  }

  function handleKeyDown(event: KeyboardEvent<HTMLLabelElement>) {
    if (disabled) {
      return;
    }

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      inputRef.current?.click();
    }
  }

  return (
    <div className={clsx(styles.root, className)}>
      <input
        ref={inputRef}
        className={styles.input}
        id={inputId}
        type="file"
        accept={accept}
        multiple={multiple}
        disabled={disabled}
        onChange={handleInputChange}
      />

      <label
        className={clsx(styles.trigger, disabled && styles.disabled)}
        htmlFor={disabled ? undefined : inputId}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-disabled={disabled}
        onKeyDown={handleKeyDown}
      >
        {children}
      </label>

      <div className={clsx(styles.files, !hasSelectedFiles && styles.placeholder)}>
        {hasSelectedFiles ? (
          <ul className={styles.fileList} aria-label="Selected files">
            {selectedFiles.map((file, index) => (
              <li className={styles.fileName} key={`${file.name}-${file.lastModified}-${index}`}>
                {file.name}
              </li>
            ))}
          </ul>
        ) : (
          <span>No files selected</span>
        )}
      </div>
    </div>
  );
}
