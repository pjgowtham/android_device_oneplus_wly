#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_vendorcompat,
    lib_fixups_user_type,
    libs_proto_3_9_1,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'hardware/oplus',
    'vendor/oneplus/sm8450-common',
    'hardware/qcom-caf/sm8450',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
]

lib_fixups: lib_fixups_user_type = {
    libs_proto_3_9_1: lib_fixup_vendorcompat,
}

blob_fixups: blob_fixups_user_type = {
    'odm/bin/hw/vendor.oplus.hardware.biometrics.fingerprint@2.1-service': blob_fixup()
        .replace_needed('android.hardware.biometrics.common-V1-ndk_platform.so', 'android.hardware.biometrics.common-V1-ndk.so')
        .replace_needed('android.hardware.biometrics.fingerprint-V1-ndk_platform.so', 'android.hardware.biometrics.fingerprint-V1-ndk.so'),
    'odm/etc/camera/CameraHWConfiguration.config': blob_fixup()
        .regex_replace('SystemCamera =  0;  0;  1;  1;  1', 'SystemCamera =  0;  0;  0;  0;  1'),
    ('odm/lib/liblvimfs_wrapper.so', 'odm/lib64/libCOppLceTonemapAPI.so', 'odm/lib64/libSuperRaw.so', 'odm/lib64/libYTCommon.so', 'odm/lib64/libaps_frame_registration.so', 'odm/lib64/libyuv2.so'): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    ('odm/lib64/libAlgoProcess.so', 'vendor/lib64/libcamximageformatutils.so'): blob_fixup()
        .replace_needed('android.hardware.graphics.common-V2-ndk_platform.so', 'android.hardware.graphics.common-V5-ndk.so')
        .replace_needed('vendor.qti.hardware.display.config-V2-ndk_platform.so', 'vendor.qti.hardware.display.config-V5-ndk.so'),
    'odm/lib64/libextensionlayer.so': blob_fixup()
        .replace_needed('libziparchive.so', 'libziparchive_odm.so'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/etc/libnfc-nxp.conf': blob_fixup()
        .regex_replace('(NXPLOG_.*_LOGLEVEL)=0x03', '\\1=0x02')
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
}  # fmt: skip

module = ExtractUtilsModule(
    'ferrari',
    'realme',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    check_elf=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, '../oneplus/sm8450-common', module.vendor
    )
    utils.run()
