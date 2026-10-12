
"""
Vyom Orchestrator - the central brain.
"""

import os
import sys

_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _folder in ["core", "memory", "security", "tools", "agents"]:
    _path = os.path.join(_base, _folder)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from llm_brain import LLMBrain
from local_llm_brain import LocalLLMBrain
from gemini_brain import GeminiBrain
from planning_engine import PlanningEngine
from memory_system import MemorySystem
from vector_memory import VectorMemory
from security_brain import SecurityBrain, UserLevel
from tool_registry import ToolRegistry, register_default_tools
from agent_router import AgentRouter, VisionAgent
from computer_control_agent import ComputerControlAgent
from live_camera_agent import LiveCameraAgent
from internet_intelligence import InternetIntelligence
from internet_browser import InternetBrowser, InternetIntelligenceLLM
from model_router import ModelRouter
from knowledge_graph import KnowledgeGraph
from autonomy import AutonomyManager, AutonomyLevel
from autonomous_worker import AutonomousWorker
from task_scheduler import TaskScheduler
from context_reliability_personalization import ContextEngine, IdentitySystem, PersonalizationEngine
from self_modification import SelfModification
from math_solver import MathSolver
from chemistry_solver import ChemistrySolver
from biology_toolkit import BiologyToolkit
from voice_brain import VoiceBrain
from wake_word_listener import WakeWordListener
from parallel_executor import ParallelAgentExecutor
from smart_home_controller import SmartHomeController
from robotics_controller import RoboticsController
from lab_equipment_controller import LabEquipmentController
from encryption import SecureVault, EncryptedMemoryWrapper
from authentication import AuthenticationSystem
from prompt_injection_guard import PromptInjectionGuard
from tamper_evident_log import TamperEvidentLog
from integrity_monitor import IntegrityMonitor, load_or_create_secret_key, IntegrityViolationError
from personality_system import PersonalityManager, Personality
from feedback_logger import FeedbackLogger


class VyomOrchestrator:
    def __init__(self, api_key=None, db_path="vyom_memory.db", mode="cloud",
                 local_model="llama3.2", local_host="localhost", local_port=11434,
                 enable_integrity_check=False):

        if enable_integrity_check:
            integrity_key_path = os.path.join(_base, "_integrity_secret.key")
            integrity_baseline_path = os.path.join(_base, "_integrity_baseline.json")
            secret_key = load_or_create_secret_key(integrity_key_path)
            self.integrity_monitor = IntegrityMonitor(
                package_root=_base,
                baseline_file=integrity_baseline_path,
                secret_key=secret_key,
            )
            self.integrity_monitor.verify_or_crash(allow_first_run_baseline=True)
        else:
            self.integrity_monitor = None

        self.mode = mode
        if mode == "local":
            self.brain = LocalLLMBrain(model=local_model, host=local_host, port=local_port)
        elif mode == "gemini":
            self.brain = GeminiBrain(api_key=api_key)
        else:
            self.brain = LLMBrain(api_key=api_key)

        self.planner = PlanningEngine(llm_brain=self.brain)
        self.memory = MemorySystem(db_path=db_path)
        self.security = SecurityBrain()
        self.tools = ToolRegistry(self.security)
        register_default_tools(self.tools)

        self.agent_router = AgentRouter(self.brain, security=self.security)
        self.vision_agent = VisionAgent(self.brain, security=self.security)
        self.live_camera = LiveCameraAgent(self.vision_agent, self.security)
        self.internet_browser = InternetBrowser()
        self.internet_intelligence_llm = InternetIntelligenceLLM(self.brain, self.internet_browser)
        self.computer_agent = ComputerControlAgent(self.security)
        self.internet = InternetIntelligence(self.brain)
        self.model_router = ModelRouter()
        self.knowledge_graph = KnowledgeGraph()
        self.autonomy = AutonomyManager(default_level=AutonomyLevel.APPROVE_THEN_ACT)
        self.scheduler = TaskScheduler()
        self.context_engine = ContextEngine(memory_system=self.memory)
        self.identity = IdentitySystem()
        self.personalization = PersonalizationEngine(self.memory)
        self.self_modification = SelfModification(self.security, package_root=_base)
        self.math_solver = MathSolver(brain=self.brain)
        self.chemistry_solver = ChemistrySolver()
        self.biology_toolkit = BiologyToolkit()
        self.voice = VoiceBrain(wake_word="vyom")

        self.wake_word_listener = WakeWordListener(self.voice, on_command=self._on_wake_word_command)
        self.parallel_executor = ParallelAgentExecutor(self.agent_router)
        self.vector_memory = VectorMemory(db_path=db_path.replace(".db", "_vectors.db"))
        self.smart_home = None
        self.robotics = None
        self.lab_equipment = LabEquipmentController(security=self.security)

        self.autonomous_worker = AutonomousWorker(
            self.planner, self.autonomy, self.security,
            user_id="default_user", user_level=UserLevel.TRUSTED,
        )

        self.secure_vault = SecureVault(key_file=db_path.replace(".db", "_secret.key"))
        self.encrypted_memory = EncryptedMemoryWrapper(self.memory.long_term, self.secure_vault)

        self.auth = AuthenticationSystem(credentials_file=db_path.replace(".db", "_credentials.json"))
        self.injection_guard = PromptInjectionGuard()
        self.tamper_evident_log = TamperEvidentLog(log_path=db_path.replace(".db", "_tamper_audit.log"))
        self.feedback_logger = FeedbackLogger(log_path=db_path.replace(".db", "_feedback.log"))

        self.personality = PersonalityManager(default=Personality.VYOM)


    def _cli_confirm(self, action, risk, details):
        print("\n[Vyom Security] Dangerous action requested: " + action + " (risk=" + risk.name + ")")
        print("Details: " + str(details))
        ans = input("Confirm? (yes/no): ").strip().lower()
        return ans in ("y", "yes", "haan", "han")

    def _on_wake_word_command(self, command):
        response = self.handle_message("voice_user", UserLevel.TRUSTED, command)
        try:
            self.voice.speak(response)
        except Exception:
            pass

    def configure_smart_home(self, base_url, access_token):
        self.smart_home = SmartHomeController(base_url, access_token, security=self.security)

    def configure_robotics(self, port="/dev/ttyUSB0", baudrate=9600):
        self.robotics = RoboticsController(port, baudrate, security=self.security)
        return self.robotics.connect()

    def handle_message(self, user_id, user_level, message):
        self.personality.detect_and_switch(message)

        if message.strip().startswith("/code "):
            instruction = message.strip()[6:]
            parts = instruction.split(" ", 1)
            if len(parts) == 2:
                file_path, real_instruction = parts
                result = self.self_modification.write_code_from_instruction(
                    self.brain, user_id, user_level, file_path, real_instruction
                )
                return str(result)
            return "Format: /code <file_path> <instruction>"

        self.memory.working.append_message("user", message)
        self.vector_memory.add(message, metadata={"role": "user", "user_id": user_id})
        self.memory.remember_fact(message, metadata={"user_id": user_id})

        context = self.memory.full_context(query=message)
        similar = self.vector_memory.semantic_search(message, top_k=5)
        extra_memory = ""
        if similar:
            extra_memory = "\n\nPurani related baatein: " + "; ".join(m["content"] for m in similar)

        system_prompt = self._build_system_prompt(context) + extra_memory

        result = self.brain.chat([{"role": "user", "content": message}], system=system_prompt)

        if "error" in result:
            return "[Vyom] " + result["error"]

        text_parts = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
        answer = "\n".join(text_parts).strip()

        self.memory.working.append_message("assistant", answer)
        self.vector_memory.add(answer, metadata={"role": "assistant", "user_id": user_id})
        self.memory.long_term.store_episode(summary="User asked: " + message[:100], outcome="success")

        return answer

    def _build_system_prompt(self, context):
        base = self.brain.system_prompt
        persona_addition = self.personality.get_system_prompt_addition()
        mem_snippet = ""
        if context.get("relevant_memories"):
            facts = "; ".join(m["content"] for m in context["relevant_memories"][:5])
            mem_snippet = "\n\nRelevant memory: " + facts
        return base + "\n\n" + persona_addition + mem_snippet

    def run_goal(self, goal, user_id, user_level):
        plan = self.planner.create_plan(goal)
        return plan.to_dict()

    def route_to_agent(self, task):
        return self.agent_router.handle(task)
