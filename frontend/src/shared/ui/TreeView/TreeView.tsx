import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
  type ReactNode,
} from 'react';
import clsx from 'clsx';

import styles from './TreeView.module.css';

export interface TreeViewNode {
  id: string;
  label: ReactNode;
  children?: TreeViewNode[];
  disabled?: boolean;
}

export interface TreeViewProps {
  nodes: TreeViewNode[];
  selectedId?: string;
  defaultExpandedIds?: string[];
  expandedIds?: string[];
  onExpandedChange?: (expandedIds: string[]) => void;
  onSelect?: (node: TreeViewNode) => void;
  className?: string;
}

interface VisibleTreeNode {
  node: TreeViewNode;
  depth: number;
  parentId?: string;
}

type TreeItemStyle = CSSProperties & {
  '--tree-view-level': number;
};

function useRovingTreeFocus({
  visibleNodes,
  selectedId,
}: {
  visibleNodes: VisibleTreeNode[];
  selectedId?: string;
}) {
  const nodeRefs = useRef(new Map<string, HTMLDivElement>());
  const initialFocusedId =
    visibleNodes.find(({ node }) => node.id === selectedId)?.node.id ?? visibleNodes[0]?.node.id;
  const [focusedId, setFocusedId] = useState<string | undefined>(initialFocusedId);

  useEffect(() => {
    if (visibleNodes.length === 0) {
      setFocusedId(undefined);
      return;
    }

    if (!focusedId || !visibleNodes.some(({ node }) => node.id === focusedId)) {
      setFocusedId(
        visibleNodes.find(({ node }) => node.id === selectedId)?.node.id ?? visibleNodes[0].node.id,
      );
    }
  }, [focusedId, selectedId, visibleNodes]);

  function focusNode(nodeId: string | undefined) {
    if (!nodeId) {
      return;
    }

    setFocusedId(nodeId);
    requestAnimationFrame(() => {
      nodeRefs.current.get(nodeId)?.focus();
    });
  }

  function focusNodeAtIndex(index: number) {
    focusNode(visibleNodes[index]?.node.id);
  }

  return {
    nodeRefs,
    focusedId,
    setFocusedId,
    focusNode,
    focusNodeAtIndex,
  };
}

export function TreeView({
  nodes,
  selectedId,
  defaultExpandedIds,
  expandedIds,
  onExpandedChange,
  onSelect,
  className,
}: TreeViewProps) {
  const parentIds = getParentIds(nodes);
  const [internalExpandedIds, setInternalExpandedIds] = useState(() =>
    normalizeExpandedIds(defaultExpandedIds, parentIds),
  );
  const isControlled = expandedIds !== undefined;
  const currentExpandedIds = normalizeExpandedIds(
    isControlled ? expandedIds : internalExpandedIds,
    parentIds,
  );
  const expandedIdSet = new Set(currentExpandedIds);
  const visibleNodes = getVisibleNodes(nodes, expandedIdSet);
  const { nodeRefs, focusedId, setFocusedId, focusNode, focusNodeAtIndex } = useRovingTreeFocus({
    visibleNodes,
    selectedId,
  });

  if (nodes.length === 0) {
    return null;
  }

  function updateExpandedIds(nextExpandedIds: string[]) {
    const normalizedExpandedIds = normalizeExpandedIds(nextExpandedIds, parentIds);

    if (!isControlled) {
      setInternalExpandedIds(normalizedExpandedIds);
    }

    onExpandedChange?.(normalizedExpandedIds);
  }

  function toggleNode(node: TreeViewNode) {
    if (node.disabled || !hasChildren(node)) {
      return;
    }

    const isExpanded = expandedIdSet.has(node.id);
    const nextExpandedIds = isExpanded
      ? currentExpandedIds.filter((id) => id !== node.id)
      : [...currentExpandedIds, node.id];

    updateExpandedIds(nextExpandedIds);
  }

  function expandNode(node: TreeViewNode) {
    if (node.disabled || !hasChildren(node) || expandedIdSet.has(node.id)) {
      return;
    }

    updateExpandedIds([...currentExpandedIds, node.id]);
  }

  function collapseNode(node: TreeViewNode) {
    if (node.disabled || !hasChildren(node) || !expandedIdSet.has(node.id)) {
      return;
    }

    updateExpandedIds(currentExpandedIds.filter((id) => id !== node.id));
  }

  function selectNode(node: TreeViewNode) {
    if (node.disabled) {
      return;
    }

    onSelect?.(node);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const currentIndex = visibleNodes.findIndex(({ node }) => node.id === focusedId);
    const safeCurrentIndex = currentIndex >= 0 ? currentIndex : 0;
    const currentVisibleNode = visibleNodes[safeCurrentIndex];

    if (!currentVisibleNode) {
      return;
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        focusNodeAtIndex(Math.min(safeCurrentIndex + 1, visibleNodes.length - 1));
        break;
      case 'ArrowUp':
        event.preventDefault();
        focusNodeAtIndex(Math.max(safeCurrentIndex - 1, 0));
        break;
      case 'ArrowRight':
        event.preventDefault();
        if (hasChildren(currentVisibleNode.node) && !expandedIdSet.has(currentVisibleNode.node.id)) {
          expandNode(currentVisibleNode.node);
        } else {
          focusNodeAtIndex(Math.min(safeCurrentIndex + 1, visibleNodes.length - 1));
        }
        break;
      case 'ArrowLeft':
        event.preventDefault();
        if (hasChildren(currentVisibleNode.node) && expandedIdSet.has(currentVisibleNode.node.id)) {
          collapseNode(currentVisibleNode.node);
        } else {
          focusNode(currentVisibleNode.parentId);
        }
        break;
      case 'Home':
        event.preventDefault();
        focusNodeAtIndex(0);
        break;
      case 'End':
        event.preventDefault();
        focusNodeAtIndex(visibleNodes.length - 1);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (hasChildren(currentVisibleNode.node)) {
          toggleNode(currentVisibleNode.node);
        } else {
          selectNode(currentVisibleNode.node);
        }
        break;
      default:
        break;
    }
  }

  function renderTreeNodes(treeNodes: TreeViewNode[], depth: number) {
    return treeNodes.map((node) => {
      const isExpanded = expandedIdSet.has(node.id);
      const isSelected = selectedId === node.id;
      const nodeHasChildren = hasChildren(node);
      const itemStyle: TreeItemStyle = {
        '--tree-view-level': depth,
      };

      return (
        <div
          ref={(element) => {
            if (element) {
              nodeRefs.current.set(node.id, element);
            } else {
              nodeRefs.current.delete(node.id);
            }
          }}
          className={clsx(styles.item, node.disabled && styles.disabled)}
          key={node.id}
          role="treeitem"
          aria-expanded={nodeHasChildren ? isExpanded : undefined}
          aria-selected={isSelected}
          aria-disabled={node.disabled}
          tabIndex={focusedId === node.id ? 0 : -1}
          data-tree-node-id={node.id}
          onFocus={() => setFocusedId(node.id)}
        >
          <div
            className={clsx(styles.row, isSelected && styles.selected)}
            onClick={() => selectNode(node)}
          >
            <span className={styles.content} style={itemStyle}>
              <span
                className={clsx(styles.indicator, nodeHasChildren && styles.expandable)}
                aria-hidden="true"
                onClick={(event) => {
                  event.stopPropagation();
                  toggleNode(node);
                }}
              >
                {nodeHasChildren ? '▸' : ''}
              </span>
              <span className={styles.label}>{node.label}</span>
            </span>
          </div>

          {nodeHasChildren && isExpanded ? (
            <div className={styles.group} role="group">
              {renderTreeNodes(node.children ?? [], depth + 1)}
            </div>
          ) : null}
        </div>
      );
    });
  }

  return (
    <div className={clsx(styles.tree, className)} role="tree" onKeyDown={handleKeyDown}>
      {renderTreeNodes(nodes, 1)}
    </div>
  );
}

function hasChildren(node: TreeViewNode) {
  return Boolean(node.children?.length);
}

function getParentIds(nodes: TreeViewNode[]) {
  const parentIds = new Set<string>();

  function visit(treeNodes: TreeViewNode[]) {
    treeNodes.forEach((node) => {
      if (hasChildren(node)) {
        parentIds.add(node.id);
        visit(node.children ?? []);
      }
    });
  }

  visit(nodes);

  return parentIds;
}

function normalizeExpandedIds(expandedIds: string[] | undefined, parentIds: Set<string>) {
  if (!expandedIds) {
    return [];
  }

  return expandedIds.filter(
    (id, index) => parentIds.has(id) && expandedIds.indexOf(id) === index,
  );
}

function getVisibleNodes(nodes: TreeViewNode[], expandedIds: Set<string>) {
  const visibleNodes: VisibleTreeNode[] = [];

  function visit(treeNodes: TreeViewNode[], depth: number, parentId?: string) {
    treeNodes.forEach((node) => {
      visibleNodes.push({ node, depth, parentId });

      if (hasChildren(node) && expandedIds.has(node.id)) {
        visit(node.children ?? [], depth + 1, node.id);
      }
    });
  }

  visit(nodes, 1);

  return visibleNodes;
}
