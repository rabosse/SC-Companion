// Custom Spaceship SVG Icon
const SpaceshipIcon = ({ className = "w-6 h-6", color = "currentColor" }) => {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {/* Main body */}
      <path d="M12 2L4 8V14L12 20L20 14V8L12 2Z" fill={color} fillOpacity="0.2" />
      {/* Cockpit */}
      <circle cx="12" cy="10" r="2" fill={color} />
      {/* Wings */}
      <path d="M4 10L2 12L4 14" strokeWidth="2" />
      <path d="M20 10L22 12L20 14" strokeWidth="2" />
      {/* Engine glow */}
      <path d="M10 18L12 22L14 18" strokeWidth="2" />
      {/* Detail lines */}
      <line x1="12" y1="2" x2="12" y2="8" strokeWidth="1.5" />
      <line x1="8" y1="12" x2="16" y2="12" strokeWidth="1" opacity="0.5" />
    </svg>
  );
};

export default SpaceshipIcon;
