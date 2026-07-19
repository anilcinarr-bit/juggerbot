import logging
from typing import Dict, Any, List
from app.models.incoming_message import IncomingMessage
from app.automation.coupon_extractor import CouponExtractor
from app.automation.message_normalizer import MessageNormalizer
from app.automation.platform_detector import PlatformDetector
from app.automation.adapter_router import AdapterRouter

logger = logging.getLogger("automation.engine")
extractor = CouponExtractor()
normalizer = MessageNormalizer()
platform_detector = PlatformDetector()
router = AdapterRouter()


class AutomationEngine:
    """Automation engine for handling browser automation triggers from Telegram messages"""
    
    async def execute(self, message: IncomingMessage) -> Dict[str, Any]:
        """
        Execute automation based on incoming Telegram message
        
        Args:
            message: The IncomingMessage that triggered the automation
            
        Returns:
            Dict containing execution results and metadata
        """
        try:
            # Log structured information about the automation trigger
            logger.info("Automation trigger received")
            logger.info(f"Source chat: {message.chat_title} ({message.chat_id})")
            logger.info(f"Sender: {message.sender_name}")
            
            # Normalize the message text before processing
            normalized_text = normalizer.normalize(message.text)
            logger.info(f"Original message: {message.text}")
            logger.info(f"Normalized message: {normalized_text}")
            
            logger.info(f"Message date: {message.date}")
            
            # Extract coupons from the normalized message text
            coupons = extractor.extract(normalized_text)
            
            if not coupons:
                logger.info("No automation triggered.")
                return {
                    "status": "no_automation",
                    "triggered_by": {
                        "chat_title": message.chat_title,
                        "chat_id": message.chat_id,
                        "sender_name": message.sender_name,
                        "sender_id": message.sender_id,
                        "message_text": message.text,
                        "message_date": message.date.isoformat() if message.date else None
                    },
                    "automation_type": "telegram_message_trigger",
                    "processed_at": "2026-07-18T00:26:35Z"
                }
            else:
                logger.info("Automation triggered.")
                
                # Log detected coupons
                logger.info("Detected coupons:")
                for coupon in coupons:
                    logger.info(coupon)
                
                # Detect platform from message and coupon
                detection_result = platform_detector.detect_platform(normalized_text, coupons[0])
                platform = detection_result.platform
                coupon_code = detection_result.coupon
                confidence = detection_result.confidence
                
                logger.info(f"Detected platform: {platform}")
                logger.info(f"Confidence: {confidence:.2f}")
                logger.info(f"Selected adapter: {platform}Adapter")
                
                # Execute the appropriate adapter for the detected platform
                result = await router.execute(platform, coupon_code)
                
                # Return structured results with coupon information and adapter execution result
                return {
                    "status": "success",
                    "triggered_by": {
                        "chat_title": message.chat_title,
                        "chat_id": message.chat_id,
                        "sender_name": message.sender_name,
                        "sender_id": message.sender_id,
                        "message_text": message.text,
                        "message_date": message.date.isoformat() if message.date else None
                    },
                    "automation_type": "telegram_message_trigger",
                    "processed_at": "2026-07-18T00:26:35Z",
                    "detected_coupons": coupons,
                    "browser_automation_result": result
                }
            
        except Exception as e:
            logger.error(f"Error executing automation: {e}")
            return {
                "status": "error",
                "error": str(e),
                "triggered_by": {
                    "chat_title": message.chat_title,
                    "chat_id": message.chat_id,
                    "sender_name": message.sender_name
                }
            }
