import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import {
    OrbitControls,
    Stars,
    Sparkles,
    Float,
    Text
} from '@react-three/drei'
import Avatar from './Avatar'

// Gold coins/treasures floating around
function TreasureParticles() {
    return (
        <Sparkles
            count={100}
            scale={10}
            size={3}
            speed={0.3}
            opacity={0.6}
            color="#ffd700"
        />
    )
}

// Dramatic spotlight
function DramaticLighting() {
    return (
        <>
            {/* Main spotlight from above */}
            <spotLight
                position={[0, 10, 5]}
                angle={0.4}
                penumbra={0.5}
                intensity={2}
                color="#ffd700"
                castShadow
            />

            {/* Backlight for rim effect */}
            <spotLight
                position={[0, 5, -8]}
                angle={0.6}
                penumbra={0.8}
                intensity={1.5}
                color="#8b5cf6"
            />

            {/* Fill lights */}
            <pointLight position={[-5, 3, 2]} intensity={0.5} color="#22d3ee" />
            <pointLight position={[5, 3, 2]} intensity={0.5} color="#ef4444" />

            {/* Ambient for visibility */}
            <ambientLight intensity={0.3} color="#1a1a2e" />
        </>
    )
}

// Vault floor with glowing ring
function VaultFloor() {
    return (
        <group>
            {/* Main floor */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]} receiveShadow>
                <circleGeometry args={[15, 64]} />
                <meshStandardMaterial
                    color="#0a0a0f"
                    metalness={0.8}
                    roughness={0.2}
                />
            </mesh>

            {/* Glowing inner ring */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.98, 0]}>
                <ringGeometry args={[2, 2.2, 64]} />
                <meshStandardMaterial
                    color="#ffd700"
                    emissive="#ffd700"
                    emissiveIntensity={0.5}
                />
            </mesh>
        </group>
    )
}

// Vault background
function VaultBackground() {
    return (
        <mesh position={[0, 0, -10]}>
            <planeGeometry args={[50, 30]} />
            <meshStandardMaterial
                color="#0a0a0f"
                metalness={0.5}
                roughness={0.8}
            />
        </mesh>
    )
}

// Loading fallback component
function LoadingFallback() {
    return (
        <mesh>
            <boxGeometry args={[0.5, 0.5, 0.5]} />
            <meshStandardMaterial color="#ffd700" emissive="#ffd700" emissiveIntensity={0.5} />
        </mesh>
    )
}

export default function Scene({ visemeData, isPlaying }) {
    return (
        <Canvas
            shadows
            camera={{ position: [0, 1, 5], fov: 50 }}
            gl={{ antialias: true }}
        >
            {/* Dark environment */}
            <color attach="background" args={['#050508']} />
            <fog attach="fog" args={['#050508', 8, 30]} />

            {/* Lighting - always visible */}
            <DramaticLighting />

            {/* Stars in background */}
            <Stars
                radius={50}
                depth={50}
                count={2000}
                factor={3}
                saturation={0.5}
                fade
                speed={0.5}
            />

            {/* Floating particles */}
            <TreasureParticles />

            {/* Vault elements - outside Suspense so they always show */}
            <VaultFloor />
            <VaultBackground />

            <Suspense fallback={<LoadingFallback />}>
                {/* Avatar with floating animation */}
                <Float
                    speed={1.5}
                    rotationIntensity={0.1}
                    floatIntensity={0.3}
                    floatingRange={[-0.1, 0.1]}
                >
                    <Avatar
                        visemeData={visemeData}
                        isPlaying={isPlaying}
                    />
                </Float>
            </Suspense>

            {/* Camera controls - limited */}
            <OrbitControls
                enableZoom={false}
                enablePan={false}
                minPolarAngle={Math.PI / 3}
                maxPolarAngle={Math.PI / 2}
                minAzimuthAngle={-Math.PI / 6}
                maxAzimuthAngle={Math.PI / 6}
            />
        </Canvas>
    )
}
