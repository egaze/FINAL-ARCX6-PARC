#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "parc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__TagOrder() -> *const std::ffi::c_void;
}

#[link(name = "parc_msgs__rosidl_generator_c")]
extern "C" {
    fn parc_msgs__msg__TagOrder__init(msg: *mut TagOrder) -> bool;
    fn parc_msgs__msg__TagOrder__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TagOrder>, size: usize) -> bool;
    fn parc_msgs__msg__TagOrder__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TagOrder>);
    fn parc_msgs__msg__TagOrder__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TagOrder>, out_seq: *mut rosidl_runtime_rs::Sequence<TagOrder>) -> bool;
}

// Corresponds to parc_msgs__msg__TagOrder
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Published by the referee on /parc/tag_order when the judge arms the run.
/// QoS: reliable, transient local, depth 1 (late subscribers still receive it).

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TagOrder {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,

    /// The order in which the tags must be visited, e.g. [7, 1, 9, 4].
    pub tag_ids: rosidl_runtime_rs::Sequence<u8>,

}



impl Default for TagOrder {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !parc_msgs__msg__TagOrder__init(&mut msg as *mut _) {
        panic!("Call to parc_msgs__msg__TagOrder__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TagOrder {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__TagOrder__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__TagOrder__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__TagOrder__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TagOrder {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TagOrder where Self: Sized {
  const TYPE_NAME: &'static str = "parc_msgs/msg/TagOrder";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__TagOrder() }
  }
}


#[link(name = "parc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__StartSignal() -> *const std::ffi::c_void;
}

#[link(name = "parc_msgs__rosidl_generator_c")]
extern "C" {
    fn parc_msgs__msg__StartSignal__init(msg: *mut StartSignal) -> bool;
    fn parc_msgs__msg__StartSignal__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<StartSignal>, size: usize) -> bool;
    fn parc_msgs__msg__StartSignal__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<StartSignal>);
    fn parc_msgs__msg__StartSignal__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<StartSignal>, out_seq: *mut rosidl_runtime_rs::Sequence<StartSignal>) -> bool;
}

// Corresponds to parc_msgs__msg__StartSignal
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Published once by the team on /parc/start when the robot starts its run.
/// QoS: reliable, depth 10. The run clock starts when the referee receives it.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct StartSignal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,


    // This member is not documented.
    #[allow(missing_docs)]
    pub method: u8,

    /// For voice starts: the recognised word ("go", "allez" or "vai"). Empty otherwise.
    pub heard: rosidl_runtime_rs::String,

}

impl StartSignal {
    /// started by a typed command
    pub const METHOD_COMMAND: u8 = 0;

    /// started by a spoken start word (bonus)
    pub const METHOD_VOICE: u8 = 1;

}


impl Default for StartSignal {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !parc_msgs__msg__StartSignal__init(&mut msg as *mut _) {
        panic!("Call to parc_msgs__msg__StartSignal__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for StartSignal {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__StartSignal__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__StartSignal__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__StartSignal__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for StartSignal {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for StartSignal where Self: Sized {
  const TYPE_NAME: &'static str = "parc_msgs/msg/StartSignal";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__StartSignal() }
  }
}


#[link(name = "parc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__TagVisit() -> *const std::ffi::c_void;
}

#[link(name = "parc_msgs__rosidl_generator_c")]
extern "C" {
    fn parc_msgs__msg__TagVisit__init(msg: *mut TagVisit) -> bool;
    fn parc_msgs__msg__TagVisit__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TagVisit>, size: usize) -> bool;
    fn parc_msgs__msg__TagVisit__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TagVisit>);
    fn parc_msgs__msg__TagVisit__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TagVisit>, out_seq: *mut rosidl_runtime_rs::Sequence<TagVisit>) -> bool;
}

// Corresponds to parc_msgs__msg__TagVisit
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Published once by the team on /parc/tag_visit at each tag, while the robot is
/// stopped in the visit pose (0.5 m from the tag, facing it within +-12 degrees).
/// After publishing, the robot must hold the pose for at least 3 seconds.
/// QoS: reliable, depth 10.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TagVisit {
    /// header.stamp: the moment of the visit. header.frame_id: the camera frame used.
    pub header: std_msgs::msg::rmw::Header,

    /// AprilTag 36h11 ID of the tag being visited (1, 4, 7 or 9).
    pub tag_id: u8,

    /// JPEG image from a robot camera in which the tag is clearly visible.
    pub image: sensor_msgs::msg::rmw::CompressedImage,

}



impl Default for TagVisit {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !parc_msgs__msg__TagVisit__init(&mut msg as *mut _) {
        panic!("Call to parc_msgs__msg__TagVisit__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TagVisit {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__TagVisit__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__TagVisit__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__TagVisit__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TagVisit {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TagVisit where Self: Sized {
  const TYPE_NAME: &'static str = "parc_msgs/msg/TagVisit";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__TagVisit() }
  }
}


#[link(name = "parc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__Finish() -> *const std::ffi::c_void;
}

#[link(name = "parc_msgs__rosidl_generator_c")]
extern "C" {
    fn parc_msgs__msg__Finish__init(msg: *mut Finish) -> bool;
    fn parc_msgs__msg__Finish__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Finish>, size: usize) -> bool;
    fn parc_msgs__msg__Finish__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Finish>);
    fn parc_msgs__msg__Finish__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Finish>, out_seq: *mut rosidl_runtime_rs::Sequence<Finish>) -> bool;
}

// Corresponds to parc_msgs__msg__Finish
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Published by the team on /parc/finish to end the run early, e.g. after
/// skipping a tag. Not needed if all four tags are reported: the referee ends
/// the run automatically after the fourth report.
/// QoS: reliable, depth 10.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Finish {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reason: u8,

}

impl Finish {
    /// the robot has done everything it is going to do
    pub const REASON_COMPLETED: u8 = 0;

    /// the robot cannot continue
    pub const REASON_GAVE_UP: u8 = 1;

}


impl Default for Finish {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !parc_msgs__msg__Finish__init(&mut msg as *mut _) {
        panic!("Call to parc_msgs__msg__Finish__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Finish {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__Finish__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__Finish__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__Finish__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Finish {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Finish where Self: Sized {
  const TYPE_NAME: &'static str = "parc_msgs/msg/Finish";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__Finish() }
  }
}


#[link(name = "parc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__RunStatus() -> *const std::ffi::c_void;
}

#[link(name = "parc_msgs__rosidl_generator_c")]
extern "C" {
    fn parc_msgs__msg__RunStatus__init(msg: *mut RunStatus) -> bool;
    fn parc_msgs__msg__RunStatus__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RunStatus>, size: usize) -> bool;
    fn parc_msgs__msg__RunStatus__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RunStatus>);
    fn parc_msgs__msg__RunStatus__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RunStatus>, out_seq: *mut rosidl_runtime_rs::Sequence<RunStatus>) -> bool;
}

// Corresponds to parc_msgs__msg__RunStatus
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Published by the referee on /parc/run_status at 2 Hz and on every change.
/// QoS: reliable, transient local, depth 1.
/// Teams can use it to confirm their start and visits were received, and should
/// stop the robot when the state is FINISHED, TIMED_OUT or TERMINATED.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RunStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,


    // This member is not documented.
    #[allow(missing_docs)]
    pub state: u8,

    /// seconds since the start signal
    pub elapsed_s: f32,

    /// 600
    pub time_limit_s: f32,

    /// same as /parc/tag_order
    pub tag_order: rosidl_runtime_rs::Sequence<u8>,

    /// tag IDs reported, in the order received (the judges' verdict is separate)
    pub tags_reported: rosidl_runtime_rs::Sequence<u8>,

    /// StartSignal.METHOD_*, valid once RUNNING
    pub start_method: u8,

    /// robot moved before the start signal
    pub false_start: bool,

}

impl RunStatus {
    /// no run in progress
    pub const IDLE: u8 = 0;

    /// order published, waiting for /parc/start
    pub const ARMED: u8 = 1;

    /// clock running
    pub const RUNNING: u8 = 2;

    /// fourth tag reported or /parc/finish received
    pub const FINISHED: u8 = 3;

    /// time limit reached
    pub const TIMED_OUT: u8 = 4;

    /// ended by a judge (safety stop, contact with a person, loss of control)
    pub const TERMINATED: u8 = 5;

}


impl Default for RunStatus {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !parc_msgs__msg__RunStatus__init(&mut msg as *mut _) {
        panic!("Call to parc_msgs__msg__RunStatus__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RunStatus {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__RunStatus__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__RunStatus__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { parc_msgs__msg__RunStatus__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RunStatus {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RunStatus where Self: Sized {
  const TYPE_NAME: &'static str = "parc_msgs/msg/RunStatus";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__parc_msgs__msg__RunStatus() }
  }
}


