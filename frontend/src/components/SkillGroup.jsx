import { memo, useState } from 'react';
import SkillCard from './SkillCard';
import SubSkillCard from './SubSkillCard';

const SkillGroup = memo(function SkillGroup({ group, onPractice }) {
  const { children } = group;
  const [expanded, setExpanded] = useState(false);

  // If no children, render as compact SkillCard
  if (!children || children.length === 0) {
    return <SkillCard summary={group} onPractice={onPractice} compact />;
  }

  return (
    <div className="space-y-2">
      {/* Root skill card — compact with expand toggle */}
      <div className="relative">
        <SkillCard summary={group} onPractice={onPractice} compact />
        {/* Expand toggle — overlaid on the card */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setExpanded(!expanded);
          }}
          className="absolute top-3 right-3 w-6 h-6 rounded-md bg-white/[0.06] border border-white/[0.08] flex items-center justify-center text-[10px] text-neutral-400 hover:text-white hover:bg-white/[0.1] transition-all"
          title={expanded ? "Ocultar sub-skills" : `${children.length} sub-skills`}
        >
          {expanded ? '▾' : `+${children.length}`}
        </button>
      </div>

      {/* Sub-skills — collapsible */}
      {expanded && (
        <div className="space-y-1.5 pl-2 border-l-2 border-white/[0.04]">
          {children.map((child) => (
            <SubSkillCard
              key={child.skill.id}
              summary={child}
              onPractice={onPractice}
            />
          ))}
        </div>
      )}
    </div>
  );
});

export default SkillGroup;
