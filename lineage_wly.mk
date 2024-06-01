#
# Copyright (C) 2021-2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit from wly device
$(call inherit-product, device/oneplus/wly/device.mk)

# Inherit some common Lineage stuff.
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

PRODUCT_NAME := lineage_wly
PRODUCT_DEVICE := wly
PRODUCT_MANUFACTURER := OnePlus
PRODUCT_BRAND := OnePlus
PRODUCT_MODEL := NE2213

PRODUCT_GMS_CLIENTID_BASE := android-oneplus

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="qssi-user 16 BP2A.250605.015 1781258386416 release-keys" \
    BuildFingerprint=OnePlus/NE2213/OP516FL1:16/BP2A.250605.015/S.3c11fd8-181a3a9-17c6449:user/release-keys \
    DeviceName=OP516FL1 \
    DeviceProduct=NE2213 \
    SystemDevice=OP516FL1 \
    SystemName=NE2213
