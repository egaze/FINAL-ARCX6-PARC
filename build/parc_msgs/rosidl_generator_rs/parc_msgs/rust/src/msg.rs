#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to parc_msgs__msg__TagOrder
/// Published by the referee on /parc/tag_order when the judge arms the run.
/// QoS: reliable, transient local, depth 1 (late subscribers still receive it).

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TagOrder {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,

    /// The order in which the tags must be visited, e.g. [7, 1, 9, 4].
    pub tag_ids: Vec<u8>,

}



impl Default for TagOrder {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TagOrder::default())
  }
}

impl rosidl_runtime_rs::Message for TagOrder {
  type RmwMsg = super::msg::rmw::TagOrder;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
        tag_ids: msg.tag_ids.into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
        tag_ids: msg.tag_ids.as_slice().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
      tag_ids: msg.tag_ids
          .into_iter()
          .collect(),
    }
  }
}


// Corresponds to parc_msgs__msg__StartSignal
/// Published once by the team on /parc/start when the robot starts its run.
/// QoS: reliable, depth 10. The run clock starts when the referee receives it.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct StartSignal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,


    // This member is not documented.
    #[allow(missing_docs)]
    pub method: u8,

    /// For voice starts: the recognised word ("go", "allez" or "vai"). Empty otherwise.
    pub heard: std::string::String,

}

impl StartSignal {
    /// started by a typed command
    pub const METHOD_COMMAND: u8 = 0;

    /// started by a spoken start word (bonus)
    pub const METHOD_VOICE: u8 = 1;

}


impl Default for StartSignal {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::StartSignal::default())
  }
}

impl rosidl_runtime_rs::Message for StartSignal {
  type RmwMsg = super::msg::rmw::StartSignal;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
        method: msg.method,
        heard: msg.heard.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      method: msg.method,
        heard: msg.heard.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
      method: msg.method,
      heard: msg.heard.to_string(),
    }
  }
}


// Corresponds to parc_msgs__msg__TagVisit
/// Published once by the team on /parc/tag_visit at each tag, while the robot is
/// stopped in the visit pose (0.5 m from the tag, facing it within +-12 degrees).
/// After publishing, the robot must hold the pose for at least 3 seconds.
/// QoS: reliable, depth 10.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TagVisit {
    /// header.stamp: the moment of the visit. header.frame_id: the camera frame used.
    pub header: std_msgs::msg::Header,

    /// AprilTag 36h11 ID of the tag being visited (1, 4, 7 or 9).
    pub tag_id: u8,

    /// JPEG image from a robot camera in which the tag is clearly visible.
    pub image: sensor_msgs::msg::CompressedImage,

}



impl Default for TagVisit {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TagVisit::default())
  }
}

impl rosidl_runtime_rs::Message for TagVisit {
  type RmwMsg = super::msg::rmw::TagVisit;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        tag_id: msg.tag_id,
        image: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Owned(msg.image)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
      tag_id: msg.tag_id,
        image: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Borrowed(&msg.image)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      tag_id: msg.tag_id,
      image: sensor_msgs::msg::CompressedImage::from_rmw_message(msg.image),
    }
  }
}


// Corresponds to parc_msgs__msg__Finish
/// Published by the team on /parc/finish to end the run early, e.g. after
/// skipping a tag. Not needed if all four tags are reported: the referee ends
/// the run automatically after the fourth report.
/// QoS: reliable, depth 10.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Finish {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,


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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Finish::default())
  }
}

impl rosidl_runtime_rs::Message for Finish {
  type RmwMsg = super::msg::rmw::Finish;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
        reason: msg.reason,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      reason: msg.reason,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
      reason: msg.reason,
    }
  }
}


// Corresponds to parc_msgs__msg__RunStatus
/// Published by the referee on /parc/run_status at 2 Hz and on every change.
/// QoS: reliable, transient local, depth 1.
/// Teams can use it to confirm their start and visits were received, and should
/// stop the robot when the state is FINISHED, TIMED_OUT or TERMINATED.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RunStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,


    // This member is not documented.
    #[allow(missing_docs)]
    pub state: u8,

    /// seconds since the start signal
    pub elapsed_s: f32,

    /// 600
    pub time_limit_s: f32,

    /// same as /parc/tag_order
    pub tag_order: Vec<u8>,

    /// tag IDs reported, in the order received (the judges' verdict is separate)
    pub tags_reported: Vec<u8>,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::RunStatus::default())
  }
}

impl rosidl_runtime_rs::Message for RunStatus {
  type RmwMsg = super::msg::rmw::RunStatus;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
        state: msg.state,
        elapsed_s: msg.elapsed_s,
        time_limit_s: msg.time_limit_s,
        tag_order: msg.tag_order.into(),
        tags_reported: msg.tags_reported.into(),
        start_method: msg.start_method,
        false_start: msg.false_start,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      state: msg.state,
      elapsed_s: msg.elapsed_s,
      time_limit_s: msg.time_limit_s,
        tag_order: msg.tag_order.as_slice().into(),
        tags_reported: msg.tags_reported.as_slice().into(),
      start_method: msg.start_method,
      false_start: msg.false_start,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
      state: msg.state,
      elapsed_s: msg.elapsed_s,
      time_limit_s: msg.time_limit_s,
      tag_order: msg.tag_order
          .into_iter()
          .collect(),
      tags_reported: msg.tags_reported
          .into_iter()
          .collect(),
      start_method: msg.start_method,
      false_start: msg.false_start,
    }
  }
}


