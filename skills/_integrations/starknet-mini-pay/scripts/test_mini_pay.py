#!/usr/bin/env python3.12
"""
Starknet Mini-Pay Test Suite
30 unit tests for core functionality

Tests cover:
- Address validation
- Uint256 conversion
- Payment links
- Invoice creation
- Transaction flow
- Error handling
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mini_pay_fixed import (
    MiniPay,
    MiniPayError,
    InvalidAddressError,
    InsufficientBalanceError,
    PaymentResult,
    Token,
)


# ==================== Fixtures ====================

@pytest.fixture
def minipay():
    """Create MiniPay instance with mocked client."""
    with patch('mini_pay_fixed.FullNodeClient') as mock_client:
        mock_client.return_value = AsyncMock()
        pay = MiniPay(rpc_url="https://rpc.testnet.starknet.io/rpc/v0_6")
        pay.client = mock_client.return_value
        yield pay


@pytest.fixture
def valid_address():
    """Return a valid test address."""
    return "0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005"


@pytest.fixture
def private_key():
    """Return a test private key."""
    return "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"


# ==================== Address Validation Tests ====================

class TestAddressValidation:
    """Test address validation functionality."""
    
    def test_valid_lowercase_address(self, valid_address):
        """Test valid lowercase address."""
        assert MiniPay.validate_address(valid_address) is True
    
    def test_valid_uppercase_address(self):
        """Test valid uppercase address (should normalize)."""
        addr = "0x053C91253BC9682C04929CA02ED00B3E423F6714D2EA42D73D1B8F3F8D400005"
        assert MiniPay.validate_address(addr) is True
    
    def test_valid_with_prefix(self, valid_address):
        """Test address with 0x prefix."""
        assert MiniPay.validate_address(valid_address) is True
    
    def test_valid_without_prefix(self):
        """Test address without 0x prefix."""
        addr = "053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005"
        assert MiniPay.validate_address(addr) is True
    
    def test_invalid_too_short(self):
        """Test address that is too short."""
        assert MiniPay.validate_address("0x123") is False
    
    def test_invalid_too_long(self):
        """Test address that is too long."""
        addr = "0x" + "a" * 70
        assert MiniPay.validate_address(addr) is False
    
    def test_invalid_hex_chars(self):
        """Test address with invalid hex characters."""
        assert MiniPay.validate_address("0xgggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg") is False
    
    def test_invalid_empty(self):
        """Test empty address."""
        assert MiniPay.validate_address("") is False
        assert MiniPay.validate_address(None) is False
    
    def test_normalize_address(self):
        """Test address normalization."""
        # With 0x
        assert MiniPay.normalize_address("0x123") == "0x123"
        # Without 0x
        assert MiniPay.normalize_address("123") == "0x123"
        # Uppercase to lowercase
        assert MiniPay.normalize_address("0xABC") == "0xabc"
        # With whitespace
        assert MiniPay.normalize_address(" 0x123 ") == "0x123"


# ==================== Uint256 Conversion Tests ====================

class TestUint256Conversion:
    """Test Uint256 conversion functionality."""
    
    def test_small_value(self):
        """Test conversion of small value."""
        value = 1000
        uint = MiniPay.to_uint256(value)
        assert uint.low == value
        assert uint.high == 0
    
    def test_large_value(self):
        """Test conversion of large value."""
        # Value > 2^128
        value = 2**130
        uint = MiniPay.to_uint256(value)
        assert uint.low == 0
        assert uint.high == 4  # 2^130 / 2^128 = 4
    
    def test_max_uint256(self):
        """Test conversion of max Uint256 value."""
        max_value = 2**256 - 1
        uint = MiniPay.to_uint256(max_value)
        assert uint.low == (2**128 - 1)
        assert uint.high == (2**128 - 1)
    
    def test_uint256_to_list(self):
        """Test Uint256 to list conversion."""
        uint = MiniPay.to_uint256(1000)
        lst = MiniPay.uint256_to_list(uint)
        assert lst == [1000, 0]
    
    def test_parse_uint256(self, minipay):
        """Test parsing Uint256 from result."""
        # Single value
        result = [1000]
        assert minipay._parse_uint256(result) == 1000
        
        # Two values (low, high)
        result = [0, 1]  # 2^128
        assert minipay._parse_uint256(result) == 2**128


# ==================== Token Tests ====================

class TestTokens:
    """Test token handling."""
    
    def test_token_enum(self):
        """Test Token enum values."""
        assert Token.ETH.value == "ETH"
        assert Token.STRK.value == "STRK"
        assert Token.USDC.value == "USDC"
    
    def test_token_addresses(self, minipay):
        """Test token addresses are correctly set."""
        assert minipay.tokens["ETH"] > 0
        assert minipay.tokens["STRK"] > 0
        assert minipay.tokens["USDC"] > 0
    
    def test_unknown_token(self, minipay):
        """Test handling of unknown token."""
        with pytest.raises(ValueError, match="Unknown token"):
            MiniPay(rpc_url="").tokens.get("INVALID")


# ==================== Balance Tests ====================

class TestBalance:
    """Test balance functionality."""
    
    @pytest.mark.asyncio
    async def test_get_eth_balance(self, minipay, valid_address):
        """Test getting ETH balance."""
        # Mock the client response
        minipay.client.get_balance = AsyncMock(return_value=10**18)
        
        balance = await minipay.get_balance(valid_address, "ETH")
        
        assert balance == 10**18
        minipay.client.get_balance.assert_called_once_with(int(valid_address, 16))
    
    @pytest.mark.asyncio
    async def test_get_usdc_balance(self, minipay, valid_address):
        """Test getting USDC balance."""
        # Mock call_contract for ERC20 balanceOf
        minipay.client.call_contract = AsyncMock(return_value=[1000000, 0])  # 1 USDC
        
        balance = await minipay.get_balance(valid_address, "USDC")
        
        # 1 USDC = 1,000,000 in smallest units
        assert balance == 1000000
    
    @pytest.mark.asyncio
    async def test_invalid_address_balance(self, minipay):
        """Test balance with invalid address."""
        with pytest.raises(InvalidAddressError):
            await minipay.get_balance("invalid", "ETH")


# ==================== Transfer Tests ====================

class TestTransfer:
    """Test transfer functionality."""
    
    @pytest.mark.asyncio
    async def test_transfer_success(self, minipay, valid_address, private_key):
        """Test successful transfer."""
        # Mock balance check
        minipay.client.get_balance = AsyncMock(return_value=10**18)
        
        # Mock account creation and sign_invoke_v3
        mock_account = AsyncMock()
        mock_response = Mock()
        mock_response.transaction_hash = 0x123
        mock_account.sign_invoke_v3 = AsyncMock(return_value=mock_response)
        
        with patch.object(MiniPay, '_create_account', return_value=mock_account):
            result = await minipay.transfer(
                from_address=valid_address,
                private_key=private_key,
                to_address="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                amount=10**17,  # 0.1 ETH
                token="ETH"
            )
        
        assert isinstance(result, PaymentResult)
        assert result.status == "PENDING"
        assert "0x123" in result.tx_hash
    
    @pytest.mark.asyncio
    async def test_transfer_invalid_address(self, minipay, private_key):
        """Test transfer with invalid address."""
        with pytest.raises(InvalidAddressError):
            await minipay.transfer(
                from_address="invalid",
                private_key=private_key,
                to_address="0x123",
                amount=100,
                token="ETH"
            )
    
    @pytest.mark.asyncio
    async def test_transfer_insufficient_balance(self, minipay, valid_address, private_key):
        """Test transfer with insufficient balance."""
        # Mock balance check to return 0
        minipay.client.get_balance = AsyncMock(return_value=0)
        
        with pytest.raises(InsufficientBalanceError):
            await minipay.transfer(
                from_address=valid_address,
                private_key=private_key,
                to_address="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                amount=10**17,
                token="ETH"
            )
    
    @pytest.mark.asyncio
    async def test_transfer_erc20(self, minipay, valid_address, private_key):
        """Test ERC20 transfer."""
        # Mock balance check
        minipay.client.call_contract = AsyncMock(return_value=[10**12, 0])  # Large balance
        
        mock_account = AsyncMock()
        mock_response = Mock()
        mock_response.transaction_hash = 0x456
        mock_account.sign_invoke_v3 = AsyncMock(return_value=mock_response)
        
        with patch.object(MiniPay, '_create_account', return_value=mock_account):
            result = await minipay.transfer(
                from_address=valid_address,
                private_key=private_key,
                to_address="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                amount=1000000,  # 1 USDC
                token="USDC"
            )
        
        assert result.status == "PENDING"


# ==================== Transaction Status Tests ====================

class TestTransactionStatus:
    """Test transaction status functionality."""
    
    @pytest.mark.asyncio
    async def test_get_status_confirmed(self, minipay):
        """Test confirmed transaction status."""
        mock_receipt = Mock()
        mock_receipt.status = "ACCEPTED_ON_L2"
        minipay.client.get_transaction_receipt = AsyncMock(return_value=mock_receipt)
        
        status = await minipay.get_transaction_status("0x123")
        
        assert status == "CONFIRMED"
    
    @pytest.mark.asyncio
    async def test_get_status_pending(self, minipay):
        """Test pending transaction status."""
        mock_receipt = Mock()
        mock_receipt.status = "PENDING"
        minipay.client.get_transaction_receipt = AsyncMock(return_value=mock_receipt)
        
        status = await minipay.get_transaction_status("0x123")
        
        assert status == "PENDING"
    
    @pytest.mark.asyncio
    async def test_get_status_rejected(self, minipay):
        """Test rejected transaction status."""
        mock_receipt = Mock()
        mock_receipt.status = "REJECTED"
        minipay.client.get_transaction_receipt = AsyncMock(return_value=mock_receipt)
        
        status = await minipay.get_transaction_status("0x123")
        
        assert status == "REJECTED"
    
    @pytest.mark.asyncio
    async def test_get_status_not_found(self, minipay):
        """Test not found transaction."""
        minipay.client.get_transaction_receipt = AsyncMock(
            side_effect=Exception("Transaction not found")
        )
        
        status = await minipay.get_transaction_status("0x123")
        
        assert status == "NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_wait_for_confirmation_timeout(self, minipay):
        """Test timeout when waiting for confirmation."""
        mock_receipt = Mock()
        mock_receipt.status = "PENDING"
        minipay.client.get_transaction_receipt = AsyncMock(return_value=mock_receipt)
        
        status = await minipay.wait_for_confirmation("0x123", max_wait_seconds=1, poll_interval=0.1)
        
        assert status == "TIMEOUT"


# ==================== Payment Link Tests ====================

class TestPaymentLinks:
    """Test payment link functionality."""
    
    def test_create_link_basic(self):
        """Test basic payment link creation."""
        from link_builder import PaymentLinkBuilder
        
        link = PaymentLinkBuilder().create(
            address="0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005"
        )
        
        assert link.startswith("starknet:")
        assert "0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005" in link
    
    def test_create_link_with_amount(self):
        """Test payment link with amount."""
        from link_builder import PaymentLinkBuilder
        
        link = PaymentLinkBuilder().create(
            address="0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005",
            amount=0.05,
            memo="coffee"
        )
        
        assert "amount=0.05" in link
        assert "memo=coffee" in link
    
    def test_parse_link(self):
        """Test parsing payment link."""
        from link_builder import PaymentLinkBuilder
        
        link = "starknet:0x123?amount=0.05&memo=coffee&token=ETH"
        data = PaymentLinkBuilder().parse(link)
        
        assert data.address == "0x123"
        assert data.amount == 0.05
        assert data.memo == "coffee"
        assert data.token == "ETH"
    
    def test_wallet_deep_links(self):
        """Test wallet deep link creation."""
        from link_builder import PaymentLinkBuilder
        
        links = PaymentLinkBuilder().create_wallet_deep_links(
            address="0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005",
            amount=0.05,
            memo="coffee"
        )
        
        assert "argent://" in links["argent"]
        assert "braavos://" in links["braavos"]
        assert "0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005" in links["argent"]


# ==================== Invoice Tests ====================

class TestInvoices:
    """Test invoice functionality."""
    
    @pytest.mark.asyncio
    async def test_create_invoice(self):
        """Test invoice creation."""
        from invoice import InvoiceManager, InvoiceStatus
        
        # Mock the database
        with patch('aioSqlite.connect', new_callable=AsyncMock) as mock_connect:
            mock_db = AsyncMock()
            mock_connect.return_value = mock_db
            mock_db.execute = AsyncMock()
            mock_db.commit = AsyncMock()
            
            async with InvoiceManager() as invoice_mgr:
                # Patch the db initialization
                invoice_mgr.db = mock_db
                
                invoice = await invoice_mgr.create(
                    payer_address="0x123",
                    amount=25.00,
                    token="USDC"
                )
                
                assert invoice.amount == 25.00
                assert invoice.token == "USDC"
                assert invoice.status == InvoiceStatus.PENDING.value
    
    @pytest.mark.asyncio
    async def test_invoice_expiry(self):
        """Test invoice expiry checking."""
        from invoice import InvoiceManager, InvoiceStatus
        import time
        
        with patch('aioSqlite.connect', new_callable=AsyncMock):
            async with InvoiceManager() as invoice_mgr:
                # Create expired invoice
                invoice = await invoice_mgr.create(
                    payer_address="0x123",
                    amount=25.00,
                    token="USDC",
                    expiry_seconds=1  # 1 second expiry
                )
                
                # Wait for expiry
                await asyncio.sleep(2)
                
                assert invoice.is_expired() is True


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Test error handling functionality."""
    
    def test_minipay_error(self):
        """Test MiniPayError exception."""
        with pytest.raises(MiniPayError):
            raise MiniPayError("Test error")
    
    def test_invalid_address_error(self):
        """Test InvalidAddressError exception."""
        with pytest.raises(InvalidAddressError):
            raise InvalidAddressError("Invalid address")
    
    def test_insufficient_balance_error(self):
        """Test InsufficientBalanceError exception."""
        with pytest.raises(InsufficientBalanceError):
            raise InsufficientBalanceError("Insufficient balance")
    
    def test_error_inheritance(self):
        """Test error inheritance hierarchy."""
        assert issubclass(InvalidAddressError, MiniPayError)
        assert issubclass(InsufficientBalanceError, MiniPayError)


# ==================== Payment Result Tests ====================

class TestPaymentResult:
    """Test PaymentResult dataclass."""
    
    def test_payment_result_creation(self):
        """Test PaymentResult creation."""
        result = PaymentResult(
            tx_hash="0x123",
            status="PENDING"
        )
        
        assert result.tx_hash == "0x123"
        assert result.status == "PENDING"
        assert result.block_number is None
        assert result.error is None
    
    def test_payment_result_with_error(self):
        """Test PaymentResult with error."""
        result = PaymentResult(
            tx_hash="0x123",
            status="FAILED",
            error="Out of gas"
        )
        
        assert result.error == "Out of gas"


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
