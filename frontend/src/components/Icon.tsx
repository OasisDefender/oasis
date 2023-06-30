import React from 'react';
import { Text, Flex, useMantineTheme, rem } from '@mantine/core';

interface IconProps extends React.ComponentPropsWithoutRef<'svg'> {
    size?: number | string;
    inverted?: boolean;
  }


export function Icon({ size, inverted, ...others }: IconProps) {
  const theme = useMantineTheme();

  return (
    <Flex justify="center" align="center" gap="xs">
        <svg style={{ display: 'inline' }} {...others} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 116 123" height={rem(size)}>
            <g fill="none" fillRule="evenodd">
                <path
                fill={inverted ? theme.white : theme.colorScheme === 'dark' ? theme.white : theme.black}
                fillRule="nonzero"
                d="M55.715,0c20.867,13.199,39.669,19.466,55.855,17.992 c2.838,57.108-18.25,90.841-55.633,104.888C19.844,109.718-1.502,77.422,0.083,17.107C19.069,18.103,37.688,14.01,55.715,0 L55.715,0L55.715,0z"
                />        
            </g>
        </svg>
        <Text fz="lg"
              sx={{ fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"' }}>
                Oasis Defender
        </Text>
    </Flex>
  );
}