import { useRef, useEffect, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

// Ready Player Me avatar URL (public sample)
// In production, replace with actual GLB URL
const AVATAR_URL = 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934fe.glb'

// Viseme to morphTarget name mapping for Ready Player Me
const VISEME_MORPH_MAP = {
    'viseme_sil': 'viseme_sil',
    'viseme_PP': 'viseme_PP',
    'viseme_FF': 'viseme_FF',
    'viseme_TH': 'viseme_TH',
    'viseme_DD': 'viseme_DD',
    'viseme_kk': 'viseme_kk',
    'viseme_CH': 'viseme_CH',
    'viseme_SS': 'viseme_SS',
    'viseme_nn': 'viseme_nn',
    'viseme_RR': 'viseme_RR',
    'viseme_aa': 'viseme_aa',
    'viseme_E': 'viseme_E',
    'viseme_I': 'viseme_I',
    'viseme_O': 'viseme_O',
    'viseme_U': 'viseme_U',
}

// Fallback avatar component when GLB fails to load
function FallbackAvatar({ isPlaying }) {
    const groupRef = useRef()
    const mouthRef = useRef()

    useFrame((state) => {
        if (groupRef.current) {
            // Idle floating animation
            groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
            groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.8) * 0.05
        }
        if (mouthRef.current && isPlaying) {
            // Mouth animation when speaking
            mouthRef.current.scale.y = 0.5 + Math.sin(state.clock.elapsedTime * 15) * 0.3
        }
    })

    return (
        <group ref={groupRef} position={[0, 0, 0]}>
            {/* Head - dark metallic sphere */}
            <mesh position={[0, 0.5, 0]}>
                <sphereGeometry args={[0.5, 32, 32]} />
                <meshStandardMaterial
                    color="#1a1a2e"
                    metalness={0.9}
                    roughness={0.2}
                    emissive="#ffd700"
                    emissiveIntensity={0.05}
                />
            </mesh>

            {/* Eyes - glowing red */}
            <mesh position={[-0.15, 0.55, 0.4]}>
                <sphereGeometry args={[0.08, 16, 16]} />
                <meshStandardMaterial
                    color="#ff0000"
                    emissive="#ff0000"
                    emissiveIntensity={2}
                />
            </mesh>
            <mesh position={[0.15, 0.55, 0.4]}>
                <sphereGeometry args={[0.08, 16, 16]} />
                <meshStandardMaterial
                    color="#ff0000"
                    emissive="#ff0000"
                    emissiveIntensity={2}
                />
            </mesh>

            {/* Mouth - animated when speaking */}
            <mesh ref={mouthRef} position={[0, 0.3, 0.42]}>
                <boxGeometry args={[0.2, 0.05, 0.05]} />
                <meshStandardMaterial
                    color="#8b5cf6"
                    emissive="#8b5cf6"
                    emissiveIntensity={1}
                />
            </mesh>

            {/* Body - dark robe */}
            <mesh position={[0, -0.5, 0]}>
                <coneGeometry args={[0.6, 1.2, 8]} />
                <meshStandardMaterial
                    color="#0a0a0f"
                    metalness={0.5}
                    roughness={0.5}
                />
            </mesh>

            {/* Crown/horns - gold accents */}
            <mesh position={[-0.3, 0.9, 0]} rotation={[0, 0, -0.3]}>
                <coneGeometry args={[0.05, 0.3, 6]} />
                <meshStandardMaterial
                    color="#ffd700"
                    emissive="#ffd700"
                    emissiveIntensity={0.5}
                    metalness={1}
                    roughness={0.2}
                />
            </mesh>
            <mesh position={[0.3, 0.9, 0]} rotation={[0, 0, 0.3]}>
                <coneGeometry args={[0.05, 0.3, 6]} />
                <meshStandardMaterial
                    color="#ffd700"
                    emissive="#ffd700"
                    emissiveIntensity={0.5}
                    metalness={1}
                    roughness={0.2}
                />
            </mesh>
        </group>
    )
}

// Main Avatar component with error handling
function AvatarWithGLB({ visemeData, isPlaying }) {
    const group = useRef()
    const meshRef = useRef()
    const { scene } = useGLTF(AVATAR_URL)

    const [currentVisemeIndex, setCurrentVisemeIndex] = useState(0)
    const [startTime, setStartTime] = useState(null)

    // Find the mesh with morph targets
    useEffect(() => {
        if (scene) {
            scene.traverse((child) => {
                if (child.isMesh && child.morphTargetDictionary) {
                    meshRef.current = child
                }
            })
        }
    }, [scene])

    // Reset when new viseme data arrives
    useEffect(() => {
        if (visemeData && visemeData.length > 0 && isPlaying) {
            setCurrentVisemeIndex(0)
            setStartTime(Date.now())
        }
    }, [visemeData, isPlaying])

    // Animate visemes each frame
    useFrame((state, delta) => {
        if (!meshRef.current || !isPlaying || !visemeData || visemeData.length === 0) {
            if (meshRef.current?.morphTargetInfluences) {
                for (let i = 0; i < meshRef.current.morphTargetInfluences.length; i++) {
                    meshRef.current.morphTargetInfluences[i] *= 0.9
                }
            }
            return
        }

        const elapsed = (Date.now() - startTime) / 1000

        let newIndex = currentVisemeIndex
        for (let i = currentVisemeIndex; i < visemeData.length; i++) {
            if (visemeData[i].time <= elapsed) {
                newIndex = i
            } else {
                break
            }
        }

        if (newIndex !== currentVisemeIndex) {
            setCurrentVisemeIndex(newIndex)
        }

        const currentViseme = visemeData[newIndex]
        if (!currentViseme) return

        const visemeName = currentViseme.viseme
        const weight = currentViseme.weight || 0.5

        if (meshRef.current.morphTargetDictionary && meshRef.current.morphTargetInfluences) {
            const dict = meshRef.current.morphTargetDictionary
            const influences = meshRef.current.morphTargetInfluences

            for (let i = 0; i < influences.length; i++) {
                influences[i] = Math.max(0, influences[i] - delta * 8)
            }

            const morphName = VISEME_MORPH_MAP[visemeName]
            if (morphName && dict[morphName] !== undefined) {
                const targetIndex = dict[morphName]
                const targetWeight = weight * 0.8
                influences[targetIndex] = Math.min(1, influences[targetIndex] + (targetWeight - influences[targetIndex]) * delta * 15)
            }
        }

        if (group.current) {
            group.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.05
        }
    })

    return (
        <group ref={group} position={[0, -1.5, 0]} scale={1.5}>
            <primitive object={scene} />
        </group>
    )
}

// Export with error boundary behavior
export default function Avatar({ visemeData, isPlaying }) {
    const [hasError, setHasError] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        // Try to preload the GLB
        const loader = new THREE.FileLoader()
        loader.load(
            AVATAR_URL,
            () => {
                setIsLoading(false)
                setHasError(false)
            },
            undefined,
            () => {
                console.warn('GLB avatar failed to load, using fallback')
                setIsLoading(false)
                setHasError(true)
            }
        )
    }, [])

    // Always show fallback for now (more reliable)
    return <FallbackAvatar isPlaying={isPlaying} />
}
