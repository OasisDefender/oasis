import { useEffect, useRef, useState } from 'react';

const LeaderLine = window.LeaderLine;

export const LeaderLineComponent = ({ startElementId, endElementId, options }) => {
  const [leaderLine, setLeaderLine] = useState(null);
  const prevOptionsRef = useRef(options);

  useEffect(() => {
    const startElement = document.getElementById(startElementId);
    const endElement = document.getElementById(endElementId);

    if (startElement && endElement) {
      const line = new LeaderLine(startElement, endElement, options);
      setLeaderLine(line);
      return () => line.remove();
    }
  }, [startElementId, endElementId]);

  useEffect(() => {
    const prevOptions = prevOptionsRef.current;
    prevOptionsRef.current = options;
    if (leaderLine && prevOptions !== options) {
      leaderLine.setOptions(options);
    }
  }, [options, leaderLine]);

  return null;
};